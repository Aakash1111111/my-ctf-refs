#!/usr/bin/env python3

import argparse
import getpass
import hashlib
import hmac
import os
import sys
import tarfile
import tempfile

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad

SALT_SIZE = 16
IV_SIZE = 16
KEY_SIZE = 32  # AES-256
HMAC_SIZE = 32  # SHA-256 HMAC
PBKDF2_ITERATIONS = 200_000
CHUNK_SIZE = 64 * 1024


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 64-byte key material via PBKDF2: first 32 bytes for AES, next 32 for HMAC."""
    return PBKDF2(
        password.encode("utf-8"),
        salt,
        dkLen=KEY_SIZE * 2,
        count=PBKDF2_ITERATIONS,
        hmac_hash_module=SHA256,
    )


def compress_folder(folder_path: str, tar_path: str):
    """Create a .tar.gz archive from a folder."""
    folder_path = os.path.normpath(folder_path)
    arcname = os.path.basename(folder_path)
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(folder_path, arcname=arcname)


def encrypt_file(input_path: str, output_path: str, password: str):
    """Encrypt a file using AES-256-CBC with PBKDF2 key derivation and HMAC-SHA256 integrity."""
    salt = get_random_bytes(SALT_SIZE)
    iv = get_random_bytes(IV_SIZE)
    key_material = derive_key(password, salt)
    aes_key = key_material[:KEY_SIZE]
    hmac_key = key_material[KEY_SIZE:]

    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    mac = hmac.new(hmac_key, digestmod=hashlib.sha256)

    with open(input_path, "rb") as f_in, open(output_path, "wb") as f_out:
        f_out.write(salt)
        f_out.write(iv)
        mac.update(salt)
        mac.update(iv)

        file_size = os.path.getsize(input_path)
        bytes_read = 0

        while True:
            chunk = f_in.read(CHUNK_SIZE)
            bytes_read += len(chunk)
            is_last_chunk = bytes_read >= file_size

            if not chunk:
                break

            if is_last_chunk:
                chunk = pad(chunk, AES.block_size)
                encrypted_chunk = cipher.encrypt(chunk)
            else:
                # Only pad on the final chunk; all other chunks must be block-aligned
                if len(chunk) % AES.block_size != 0:
                    # Read remainder to align (rare with 64KB chunks, but safe-guard)
                    remainder = f_in.read(
                        AES.block_size - (len(chunk) % AES.block_size)
                    )
                    bytes_read += len(remainder)
                    chunk += remainder
                encrypted_chunk = cipher.encrypt(chunk)

            f_out.write(encrypted_chunk)
            mac.update(encrypted_chunk)

        f_out.write(mac.digest())


def decrypt_file(input_path: str, output_path: str, password: str):
    """Decrypt a file produced by encrypt_file(), verifying HMAC integrity first."""
    file_size = os.path.getsize(input_path)
    if file_size < SALT_SIZE + IV_SIZE + HMAC_SIZE:
        raise ValueError("File too small to be a valid encrypted archive.")

    with open(input_path, "rb") as f_in:
        salt = f_in.read(SALT_SIZE)
        iv = f_in.read(IV_SIZE)
        ciphertext_size = file_size - SALT_SIZE - IV_SIZE - HMAC_SIZE
        ciphertext = f_in.read(ciphertext_size)
        stored_tag = f_in.read(HMAC_SIZE)

    key_material = derive_key(password, salt)
    aes_key = key_material[:KEY_SIZE]
    hmac_key = key_material[KEY_SIZE:]

    mac = hmac.new(hmac_key, digestmod=hashlib.sha256)
    mac.update(salt)
    mac.update(iv)
    mac.update(ciphertext)
    computed_tag = mac.digest()

    if not hmac.compare_digest(computed_tag, stored_tag):
        raise ValueError(
            "Integrity check failed: wrong password or corrupted/tampered file."
        )

    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    decrypted_padded = cipher.decrypt(ciphertext)
    decrypted = unpad(decrypted_padded, AES.block_size)

    with open(output_path, "wb") as f_out:
        f_out.write(decrypted)


def extract_tar(tar_path: str, dest_dir: str = "."):
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=dest_dir)


def do_encrypt(folder: str, password: str):
    if not os.path.isdir(folder):
        print(f"Error: '{folder}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    folder = folder.rstrip(os.sep)
    base_name = os.path.basename(os.path.normpath(folder))
    output_file = f"{base_name}.tar.gz.aes256"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tar_path = os.path.join(tmp_dir, f"{base_name}.tar.gz")
        print(f"Compressing '{folder}' -> {os.path.basename(tar_path)} ...")
        compress_folder(folder, tar_path)

        print(f"Encrypting -> {output_file} ...")
        encrypt_file(tar_path, output_file, password)

    print(f"Done. Encrypted archive written to: {output_file}")


def do_decrypt(archive: str, password: str, extract: bool):
    if not os.path.isfile(archive):
        print(f"Error: '{archive}' not found.", file=sys.stderr)
        sys.exit(1)

    if archive.endswith(".tar.gz.aes256"):
        tar_output = archive[: -len(".aes256")]
    else:
        tar_output = archive + ".tar.gz"

    print(f"Decrypting '{archive}' -> {os.path.basename(tar_output)} ...")
    try:
        decrypt_file(archive, tar_output, password)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Decrypted archive written to: {tar_output}")

    if extract:
        print(f"Extracting '{tar_output}' ...")
        extract_tar(tar_output)
        os.remove(tar_output)
        print("Extraction complete. Temporary tar.gz removed.")


def main():
    parser = argparse.ArgumentParser(
        description="Compress a folder with tar+gzip and encrypt/decrypt it with AES-256."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--encrypt", metavar="FOLDER", help="Folder to compress and encrypt"
    )
    group.add_argument(
        "--decrypt", metavar="ARCHIVE", help="Encrypted .tar.gz.aes256 file to decrypt"
    )
    parser.add_argument(
        "--password",
        help="Password for encryption/decryption. If omitted, you'll be prompted securely.",
    )
    parser.add_argument(
        "--extract",
        action="store_true",
        help="When used with --decrypt, automatically extract the tar.gz after decrypting.",
    )

    args = parser.parse_args()

    password = args.password
    if not password:
        password = getpass.getpass("Password: ")
        if args.encrypt:
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                print("Error: passwords do not match.", file=sys.stderr)
                sys.exit(1)

    if args.encrypt:
        do_encrypt(args.encrypt, password)
    elif args.decrypt:
        do_decrypt(args.decrypt, password, args.extract)


if __name__ == "__main__":
    main()

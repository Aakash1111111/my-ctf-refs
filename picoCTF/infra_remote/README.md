# Remote Infrastructure

This directory contains an automated way of deploying the picoCTF platform to
a remote cloud provider. Before attempting to use this configuration we strongly
recommend you familiarize yourself with the provided [local infrastructure][il].

This remote infrastructure provisions and configures the same two machine (`web`
and `shell`), but uses `terraform`, not `vagrant`, to create the necessary
"hardware" on AWS. Aside from this change in how the machines are created all of
the [ansible][a] automation remains the same. 

This configuration is intended to serve as a demonstration of a simple remote
deployment. Similar to the local infrastructure it automates account creation,
challenge loading, and starting an event. To this it adds automated SSL/TLS
certificates and shows how you can securely integrate secret storage with our
automation. Minor modification would make it suitable for running a remote
testing or production environment for a public event. Additionally you could
update the terraform configuration to switch to an alternate cloud provider.

[il]:../infra_local
[a]:../ansible

## Assumptions

This guide assumes the following:

- cloned the repository
- have `ansible` and `terraform` installed locally
- have AWS credentials
- have shared ssh keys

##  Quick Start

From your local machine (make sure the assumptions above are met).

1. In the [terraform directory][td] edit `variables.tf` and `terraform apply`.
    - This creates the virtual machines on AWS
    - Read through the [terraform/README.md][tr] for more details.

[tr]:./terraform/README.md
[td]:./terraform

2. In this directory edit `inventory.yml`.
    - The minimal thing you will need to edit are the `ansible_host` for both
    `shell` and `web`.
    - These can be domain names or IP addresses. We recommend domain names so
    you can use the automated HTTPS support.
    - Manually configure your DNS records using the IP addresses provided in the
    `terraform` output.

3. Generate secure secrets and credentials to be stored in an `ansible-vault`.
    ```
    ./gen_vault.py
    ```

4. Provision the infrastructure.
    ```
    ansible-playbook bootstrap.yml
    ```

Once that successfully completes your CTF should be up and running.

5. Browse to your web address and login with the automatically created
   administrator account: `ctfadmin`. Get the password from your newly created
   vault. It is the `vault_web_admin_pw` value.
    ```
    ansible-vault view vault.yml
    ```

## Ansbile and Terraform

Tested using `ansible 2.9.9` from [provider][ap].

[ap]:https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible-on-ubuntu

Using `Terraform v0.12.24` from [provider][t]

[t]:https://www.terraform.io/downloads.html


## Secure Secrets (ansible-vault)

In a production setup you will have a number of sensitive variables such as
passwords and secret values. In order to store these securely, while still
allowing automation, we use ansible-vault. With ansible-vault your secrets are
stored in an  encrypted file and only decrypted with a password when a playbook
is run. For more information please consult the [documentation][ad]

[ad]:http://docs.ansible.com/ansible/playbooks_vault.html

In order to make this process smooth, we have provided a script
(`./gen_vault.py`) which chooses random values for all necessary secrets and
passwords and properly encrypts them to produce `vault.yml`.

Similar to the terraform state, this file is ignored from git by default.
However, if you are working with others you almost certainly want to commit it
to the repository either with `git add -f vault.yml` or editing the
`/.gitignore` file. So long as you used a secure password, it is safe to commit
this file since it is encrypted. At the very least you likely want to backup or
save the credentials from this file.

### Vault Password

The current setup balances convenience with security and writes your password to
a plain text file (`vault_pass.txt`) which is then loaded by default in the
`ansible.cfg`. You should not commit this file (it is `.gitignore`'d by
default). If you do not like this behavior you can remove the file and edit
`ansible.cfg` to instead prompt you or use one of the other mechanisms for
providing a `vault-pass`.

### View your secrets

```
ansible-vault view vault.yml
```

### Edit your secrets

Currently the picoCTF automation does not support changing all secrets in an
automated fashion.

If you have an existing platform deployed and want to change your credentials it
is recommend that you do so manually and then update the `vault.yml` with:

```
ansible-vault edit vault.yml
```

### Re-key your vault

Re-keying is the process of changing the password that secures your vault. It
does not change any of the protected secrets.

```
ansible-vault rekey vault.yml
```

Once you do this you will need to update `vault_pass.txt` with your new password
(if you are using it).

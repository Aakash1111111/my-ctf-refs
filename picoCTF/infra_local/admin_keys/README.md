# Keys

A common way of authenticating to a remote machine over SSH is to use _keys_.

By adding your *public* key to a remote host, you can then ssh without
a password. This is convenient and secure.

To have your personal SSH key added to the vagrant VM follow these steps.

1. Add your your SSH *public* key to this directory

`user.pub`
```
ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA6NF8iallvQVp22WDkTkyrtvp9eWW6A8YVr+kz4TjGYe7gHzIw+niNltGEFHzD8+v1I2YJ6oXevct1YeS0o9HZyN1Q9qgCgzUFtdOKLv6IedplqoPkcmF0aYet2PkEDo3MlTBckFXPITAMzF8dJSIFo9D8HfdOV0IAdx4O7PtixWKn5y2hMNG0zQPyUecp4pzC6kivAIhyfHilFR61RGL+GPXQ2MWZWFYbAGjyiYJnAmCP3NOTd0jMZEnDkbUvxhMmBYSdETk1rRgm+R4LOzFUGaHqHDLKLX+FIPKcF96hrucXzcWyLbIbEgE98OHlnVYCzRdK8jlqm8tehUc9c9WhQ== vagrant insecure public key
```

2. Update the `inventory.yml` to include the path to the key.

```
admin_keys: ["./admin_keys/user.pub"]
```

3. Re-run the provisioning steps

```
vagrant reload --provision
```

or

```
ansible-playbook site.yml
```

## WARNING

You should only ever include your SSH *public* key, not your _private_ key. If
you see a line like the following you are using the wrong key.

```
-----BEGIN RSA PRIVATE KEY-----
```

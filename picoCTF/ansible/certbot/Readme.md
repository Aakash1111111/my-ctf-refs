# certbot

Installs `certbot` to allow convenient usage of HTTPS with certificates from
Let's Encrypt.


## Certificate Requests

On it's own this role only installs `certbot` so it can be used. You need to
explicitly request certificates in your nginx tasks. This role provides a tasks
file, `request_certificates`, which can be used to request a certificate.

```
- name: Request certificate (certbot)
  vars:
    certbot_domain: "{{nginx_server_name}}"
  include_role:
    name: certbot
    tasks_from: request_certificates
  when: enable_certbot | bool
```

- `certbot_email`: email address to receive certificate notifications from
Let's Encrypt. (required, no default)
- `certbot_domain`: domain to request certificate for

# Docker

This role configures a backend host to support `DockerChallenge` style
challenges for the picoCTF platform.

It serves 3 primary purposes:

1. Install `docker` daemon and necessary dependencies.
2. Configure the `docker` daemon to listen securely on the network.
3. Utility scripts to generate client certificates and prune containers.

## 1. Docker Install

This role installs `docker.io` and `docker-compose` from the default Ubuntu
repositories.

## 2. Docker TLS Configuration

This role configures a docker daemon to also listen securely on the network by
utilizing a custom Certificate Authority and validating clients over TLS per the
[Documentation](https://docs.docker.com/engine/security/https/).

This role can be configured by setting the Common Name (CN) and the Subject
Alternative Name (SAN) for the server. These must be appropriately set and match
the host's information. For example:

```
server_CN: "docker.example.com"
server_SAN: "DNS:docker.example.com,DNS:localhost,IP:10.0.0.30,IP:127.0.0.1"
```

By default this configures the server to listen on all interfaces on port `2376`
as well as the default unix socket. These settings can be overridden either of
the following settings:

```
socket_host: "-H unix:///var/run/docker.sock"
tcp_host: "-H=0.0.0.0:2376"
```

The default docker socket allows standard users on the machine to use docker
without any modifications. The role also copies the necessary certificates and
keys so that a client could correctly authenticate to the TCP port as described
in the [documentation][sec]:

[sec]:https://docs.docker.com/engine/security/https/#secure-by-default

```
export DOCKER_HOST=tcp://$HOST:2376 DOCKER_TLS_VERIFY=1
docker ps
```

### 3. Clients and Utilities

This role also includes a playbook to generate additional client certificates as
well as to configure a specific user. Also it creates a picoCTF specific cron
job to manage the lifetime of expired containers.

The `gen_client` tasks will create the key and a certificate signed by the
custom CA. It will then fetch the necessary files back to the control machine.
This should be run against the docker host configured above.

The `config_user` tasks appropriately deploys the keys and certificates to the
client machine in the specified user's home directory.

An example of how these can be used is as follows.

```
- name: Generate docker client certs
  import_role:
    name: pico-docker
    tasks_from: gen_client
  vars:
    client: challenge.example.com
  delegate_to: docker

- name: Deploy docker client certs
  import_role:
    name: pico-docker
    tasks_from: config_user
  vars:
    user : "{{ansible_user}}"
    client: challenge.example.com
```

All of this is performed automatically in the provided example environments.

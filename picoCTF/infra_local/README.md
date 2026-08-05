# Local Infrastructure

This configuration shows how you can deploy the picoCTF platform in local
virtual machines with `vagrant`. Specifically this is the configuration and
`ansible` inventory that are used by the default `Vagrantfile`.

If you are using this as a development environment, either to work on the
picoCTF platform or develop challenges, you should not need to modify any files
in this directory.

If you are looking to use the local Vagrant VMs for some other purpose, such as
a local event, you will want to make a copy of this `infra_local` directory and
modify the configurations accordingly (e.g. setting passwords). If you are
interested in additional configuration parameters, please consult the example in
the [infra_remote][ir] directory.

[ir]:../infra_remote

## Usage

**1. Build the virtual machines and install the picoCTF platform.**

```
vagrant up
```

Once this completes you can interact with the virtual machines using the
following `vagrant` commands. For example, to get a terminal on the `shell`
server.

```
vagrant ssh shell
```

To reload the virtual machines and ensure the picoCTF platform is properly
installed and configured.

```
vagrant reload --provision
```

For more information on using `vagrant` consult the [documentation][vd].

[vd]:../docs/vagrant.md

**2. Use `ansible` to apply changes.**

This is the preferred way of interacting with the machines once they are created
(as opposed to using `vagrant` or `ssh`). By using the provided playbooks you
ensure that all of your changes are replicable and will work just as well in
a remote production environment.

This requires you either have `ansible` installed on your local machine, or that
you run these commands from within the vagrant VMs. 

```
ansible-playbook  site.yml
```

Will run all the platform provisioning steps on both `web` and `shell`. This
will take some time and is essentially what is performed the first time you run
`vagrant up` or `vagrant reload --provision`

You can limit the tasks to just a single host:

```
ansible-playbook site.yml --limit web
```

As well as run just a portion of the playbook (e.g. just the `pico-web` tasks).
This will speed up the process.

```
ansible-playbook site.yml --limit web --tags web
```

### Common Dev tasks with ansible

The following examples show how you can use the convenient `ansible` tags to run
only the relevant steps you want to speed up the development process. Please see
the [Ansible Readme](../ansible/README.md) for more tag information.

Update the static web files, for example after editing the HTML/CSS/JSX under
[picoCTF-web/web][web].

```
ansible-playbook site.yml --limit web --tags web-static
```

Update the web API, for example after editing the python under
[picoCTF-web/api][api]

```
ansible-playbook site.yml --limit web --tags web-api
```

Update `shell_manger`/`hacksport`

```
ansible-playbook site.yml --limit shell --tags shell-api
```

You can also run one-off, ad-hoc, commands with ansible (without having to
manually ssh to a machine):

```
ansible -become -a 'shell_manager status' shell
```

[web]:../picoCTF-web/web/
[api]:../picoCTF-web/api/

### Modifying the local infrastructure virtual machines

There are now quick ways to change the storage, memory, number of CPUs and IP addresses
and run multiple instances. Start by running a command like the following.

- `J` is the number of CPUs
- `M` is the amount of memory in GB
- `SIP` is shell IP address (default is 192.168.2.2)
- `WIP` is web IP address (default is 192.68.2.3)
- `SHELL_DISK_SIZE` specifies the size for the `/` partition for the shell server. Defaults to 10GB

```
J=2 M=6 SIP=192.168.2.53 WIP=192.168.2.52 SHELL_DISK_SIZE=20GB vagrant up shell && SIP=192.168.2.53 WIP=192.168.2.52 vagrant up web
```

*Warning*: If you utilize `WIP` or `SIP` you will need to always set those
environment variables whenever running any `vagrant` or `ansible` commands.

## Organization

- `ansible.cfg`: points to the relevant roles from both core `picoCTF` as well
- `inventory.yml`: sets all the configurable variables for platform deployment
- `site.yml`: main playbook used to configure the picoCTF platform

### inventory.yml

This inventory file serves to specify two important things.

1. Hosts
2. Variables

Since this inventory is already configured for the local development environment
you should not need to make any changes, however a better understanding will
help you understand the configurable options that are available with the picoCTF
platform.

**Hosts**. These are the machines created with the provided `Vagrantfile`. This
specifies how `ansible` can connect to the machines. In the default case
`vagrant` will set each machine up with a custom `private_key` file. This allows
`vagrant ssh` to work. We also use this key to connect to the machines without
needing a password.

**Variables**. These are configurable options which determine how the platform
is deployed. Again in the local development environment these are tailored for
convenience (e.g. automatically add a shell server and challenges) as well as
simplicity (e.g. no passwords) and should not need to be changed.

### site.yml

This is an `ansible` "playbook". A playbook  matches hosts from the inventory to
the "roles" which should be run on them.

For example:

```
- hosts: shell
  become: yes
  become_method: sudo
  roles:
    - {role: common     , tags: ["common"]}
    - {role: pico-docker, tags: ["docker"]}
    - {role: pico-shell , tags: ["shell"]}
```

This causes the tasks from the `common`, `pico-docker`, and `pico-shell` roles
to run on the `shell` host. Ansible knows how to connect to the `shell` host
because it is configured in the `inventory.yml` hosts section. These roles
perform all the necessary steps to setup a picoCTF shell server, including
installing the `shell_manger` utility, the custom SSH pam modules, and
a `docker` daemon. These roles are configurable by the vars section of the
`inventory.yml`

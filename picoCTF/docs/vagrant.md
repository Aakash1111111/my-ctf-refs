# Vagrant

This project uses [Vagrant](https://www.vagrantup.com/) to configure
a reproducible development environment.

The `Vagrantfile` in the top level of this repository will launch a minimal two
machine setup (`web` and `shell`) configured for easy local development.
This will most likely be the primary setup you are interested in.

These virtual machines are  automatically be provisioned using the provided
[ansible](../ansible) playbooks.

## Usage

When run from the directory containing a `Vagrantfile`

- `vagrant up`
  - On first run this will download a base Ubuntu machine, install, and
  configure the picoCTF platform. This may take some time depending on your
  network speeds.
  - On future runs, this will ensure both virtual machines are started. This
  should perform quickly.
  - Ensures networking is properly configured and synced directories are up to
  date.

- `vagrant ssh web` or `vagrant ssh shell`
  - Will provide you a shell within the relevant virtual machine.

- `vagrant reload`
  - Restarts the virtual machines.
  - Note, if you manually restart the machines with the GUI, `reboot`, or
  `shutdown -r` networking and synced folders may not function correctly. You
  want to use vagrant to preform this function.
  - You can use the `--provision` flag to re-run all the configuration steps.

- `vagrant halt`
  - Shuts down the running virtual machines. They can be brought back up with
  with `vagrant up`

There are the most common commands you will use to interact with `vagrant`, for
anything else please consult `vagrant -h` or the documentation.

## Resource Considerations

One great feature of Vagrant is it allows you to make the most of your
computer's resources, no matter how large or small. Since it is so easy to start
and stop the virtual machines, it is recommended that when you are not using
them you stop them with `vagrant halt`. This will prevent your CPU and Memory
from being used. When you want to use it again it's just a `vagrant up` away.

If you want to try an alternative configuration but are concerned all the
virtual machines will take up too much space, you can always completely remove
them with `vagrant destroy`. Note if you destroy a virtual machine you will
loose all competition state (e.g. users/solves).

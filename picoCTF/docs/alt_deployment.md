# Alternative Deployments

This repository provides an example of both a [local][.il] and a [remote][ir]
infrastructures.  We strongly recommend you familiarize yourself with these
options before considering an alternative deployment as they will provide a good
set of examples you can build from.

[il]:../infra_local
[ir]:../infra_remote

While these are the only two explicitly supported options it is entirely
possible that neither of these suite your needs and you will want to make some
changes (we certainly do when we deploy the platform for large scale events).
The good news is that since much of the deployment is automated and configurable
you should have to make relatively few changes to get started.

As an example, for a live event you may want to have:
- A [local][il] Vagrant based _development environment_
- A [remote][ir] Terraform based _testing environment_ with restricted access (e.g.
network security restrictions, or HTTP basic authentication)
- A [remote][ir] Terraform based _production environment_ with multiple tiers

To achieve this you can use the provided [local][li] and [remote][ir]
infrastructure examples as a starting point, make a copy, and then make your
modifications. Alternatively you can roll your own infrastructure and the rest
of this documentation provides you notes on successfully integrating the picoCTF
platform.

There are two keys components to a deployment. The **hardware** (or virtual
hardware) and the **software** configuration. This documentation will talk
through both.

## Hardware

In the example infrastructures provided the picoCTF platform is deployed in
a two virtual machine configuration. In both cases the creation of these virtual
machines is automated, with `vagrant` and `terraform` respectively. While the
examples target `Virtualbox` locally, and `AWS` remotely there is nothing
special about these providers. You can certainly deploy picoCTF to alternative
platforms (e.g. `vsphere`)  or providers (e.g. `gcp` or Digital Ocean), you will
just need to create the corresponding configuration or manually provision those
resources. The picoCTF platform can also be deployed to existing machines or
bare-metal physical hardware if you desire.

### Architecture

As mentioned, the provided configurations are setup with two servers `web` and
`shell`. The `web` server hosts the API and the database. The `shell` server
hosts the challenges, on-demand docker instances, and competitor shell access.
We believe this two server configuration is the minimal desirable setup in order
to isolate user and competition data from the server that provides users an
account and vulnerable challenges. You could certainly use more than just two
servers. For example having a stand alone database server or docker server.

### Alternatives

If you are looking to run an event locally (e.g. from your computer), consider
making a copy of the `infra_local` directory and modifying the `Vagrantfile` as
necessary. Since the provided configuration is setup for development purposes
you will want to make sure to lock down this configuration (e.g. set passwords)
by editing the `inventory.yml`.

If you are looking to run an event remotely (e.g. from on AWS) consider making
a copy of the `infa_remote` directory and modifying the terraform configuration
to suite your needs (e.g. scale).

If you are looking to manually configure existing machines (e.g. using neither
`vagrant` or `terraform`) then you should start with the `infra_remote`
configuration and just skip the `terraform` parts.

### Requirements

Regardless of the approach you choose to provision your hardware (automated or
manual) they key requirement is that it has the following baseline software
configuration. Both of the provided configurations ensure this.

- Operating System: Ubuntu Bionic, 18.04, amd64 server
- User account with an authorized ssh key.

OS. While the picoCTF platform can likely deploy against alternative Linux
operating systems, this is the only tested and supported base. All current
configuration automation assumes Ubuntu.

Once you have hardware (virtual or physical) that meets these requirements you
are ready to configure the software on it.

## Software

At it's core the picoCTF platform is as python [web application][web] and python
library and command line tool for [challenge management][shell]. However, in
order to pull these components together and enable functionality like competitor
accessible shell accounts there are broad system-wide configuration changes. To
facilitate this complex orchestration we utilize [ansible][] to ensure all
pieces are properly configured in an automated and repeatable fashion.

[web]:../picoCTF-web/
[shell]:../picoCTF-shell/
[ansible]:../ansible

Regardless of how you generate your hardware we strongly encourage you to
utilize the provided automation. Fortunately this is as simple as making a copy
of the provided configuration (`infa_remote` directory) and updating the
configuration to point it towards your hosts (e.g. hostnames and keys).

In the simplest setup you can run `ansible` from your local machine to configure
the remote hosts. For more complex events, or if you have multiple
administrators for your infrastructure, you might want to consider performing
these actions from a "jump box" in order to simplify synchronization and
increase performance in a cloud environment.

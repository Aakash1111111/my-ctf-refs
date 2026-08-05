# Terrafrom Notes

These notes cover how to use [Terraform](https://www.terraform.io/) to deploy
the picoCTF platform to [Amazon Web Services](https://aws.amazon.com/) (AWS).
We use Terraform to standardize, and version control the configuration of our
remote servers. This is like Vagrant for the cloud.

If you are not familiar with Terraform, it is recommended that you read through
through the [introduction](https://www.terraform.io/intro/index.html) and
[getting started](https://www.terraform.io/intro/getting-started/install.html)
prior to deploying picoCTF.

Getting picoCTF deployed to AWS is a two step process. Terraform is the first
step to create the virtual machines and configure networking, however this does
not actually install or launch the picoCTF platform. For that second step please
see the [Production Environment Readme](../README.md).

## **WARNING**

Following this guide will create real resources on AWS that will cost money.
This may only be a few dollars, but we're not responsible for any charges that
may incur.  If you're not using your AWS resources be sure to destroy them so
you are not charged.  You should check your bill regularly, especially if this
is your first time running a live CTF.

## Pre-Requisites

1. AWS
  - A deployment specific [Identity and Access Management (IAM)] account with at
    least the `AmazonEC2FullAccess` permission.
  - The following authentication variables `ACCESS_KEY_ID` and `SECRET_ACCESS_KEY`
    for the account.

2. Terraform
  - Follow the installation [instructions][tfi] on your local host.

3. Deployment SSH key
  - This key will be authorized the virtual machines you create on AWS and will allow `ssh` access.

[iam]:https://console.aws.amazon.com/iam/home
[tfi]:https://www.terraform.io/intro/getting-started/install.html

## Quick Start

This quick start is for a Linux system but the steps should be generally
applicable. At a high level it is as simple as:

1. Updating configurations
2. Running Terraform

### 1. Configuration

Add your AWS credentials for a `picoCTF` profile (or update in `variables.tf`)

`~/.aws/credentials`
```
[picoCTF]
aws_access_key_id=XXX_KEY_ID_______XXX
aws_secret_access_key=XXX__SECRET__________________________XXX
```

Ensure you have a local ssh key pair that will be added to the AWS machines you
can generate a unique key pair with the following commands or update
`public_key_path` in `variables.tf` to use an existing key

```
ssh-keygen -f ~/.ssh/picoCTF_production_rsa -C "admin@picoCTF_production" -N ""
```

Finally make any additional changes  to `variables.tf` that you might need. The
most common thing to change will be the "type" of the virtual machine instances
that you are using. This specifies the resources available (and the price).

### 2. Terraform

```
terraform init
terraform apply
```

Following these steps will automatically create the following resources on AWS:

1. Virtual Private Cloud (VPC) aka a private network
2. Internet Gateway, Routes, Subnets
3. Security Groups (aka firewall rules)
4. Instances (aka virtual servers)
5. Instance Related resources like Elastic IP addresses and Elastic Block Storage

If that completed successfully, you now have two servers (`web` and `shell`)
running on AWS ready to host your competition. The IP addresses should have been
provided at the completion of `terraform apply`. This is the bare-bones virtual
"hardware" necessary to run picoCTF remotely on AWS. However these instances
have none of the required software installed. At this point go back up to the
[infra_remote/README.md][ir] in order to continue configuring your production
picoCTF deployment.

[ir]:../README.md

**NOTE:** You might not see these resources in your [AWS EC2 Dashboard][dash] if
your region does not match the region in which you created your terraform
instances.  The terraform default is **us-east-1 (N. Virgina)**. You can change
your AWS default region using the dropdown menu to the left of support (to the
right of your user-name).

[dash]:https://console.aws.amazon.com/ec2/v2/home?region=us-east-1

You should be able to ssh into your remote instances at this point. By default,
this script uses `~/.ssh/picoCTF_production_rsa` as your ssh key, and `ubuntu`
is the default user account for Ubuntu bionic 18.04 LTS. As such, you can test
SSH using the following command:
    
```
ssh -i ~/.ssh/picoCTF_production_rsa ubuntu@<instance-elastic-IP-address>
```

If you just wanted to test this script and are not ready to run a competition
you should be sure to destroy all the resources that where created.  Don't worry
it's just as easy to get them back later thanks to the power of Terraform. To
destroy the servers and resources that where created run:

```
terraform destroy
```

Please consider reading along for a more in depth explanation of how our
Terraform configuration is structured. Also this will discuss how you can modify
the configuration to meet your needs.

## Overview of Files

The Terraform configuration is broken down into three primary parts:

1. Configurable options.
2. Resources which specify the "hardware" for the picoCTF infrastructure.
3. State

### 1. Configurable Options (`variables.tf`)

We have organized our `terraform` setup so that any change you might need to
make are isolated to this single file. This is where you would specify which SSH
key to add, or things like the machine type.

### 2. Terraform Resources (`main.tf` and `security_groups.tf`)

These are the main files which specify the resources which will be created. For
a simple setup there should be no need to edit these files. However, if for some
reason you wanted a more complex deployment you could add a server here.

These resourced are created when you run `terraform apply`. If you make any
changes you will need to run that command again in order for them to be
created/updates.

### Terraform State (`terraform.tfstate`)

This tracks your currently created resources (virtual "hardware"). This file is
created after you have run `terrafrom apply`.

[State][state] is a particularly important part of using Terraform . By default
this is stored in this directory as `terraform.tfstate`. This is how Terraform
knows what resources have been created and what their status. If you don't have
this file Terraform will no longer be able to manage your resources and you may
have to go into the [AWS Management Console][console] and manually modify/remove
orphaned elements.

[console]:https://console.aws.amazon.com
[state]:https://www.terraform.io/docs/state/

This repository defaults to ignore `terraform.tfstate` from version control.
This is the simplest and works well when there is a single person responsible
for deploying your infrastructure.  If a second member of the team wants to
modify the current infrastructure they will need to manually copy the
`terraform.tfstate` file out of band.

Another method is to commit `terraform.tfstate` into version control. This works
well for when you are developing and deploying from a private copy of the
repository. Then on every change the `terraform.tfstate` file would be committed
and tracked so all users could deploy. To add the `.tfstate` files you can
either edit the default `.gitignore` file or use `git add -f *.tfstate`.

## Common Tasks

### Basic Workflow

1. Make edits to the appropriate configuration file
2. Check what changes it will have
    - `terraform plan`
    - look for things like improperly templated/applied variables
3. Apply the changes
    - `terraform apply` 
4. If you are tracking `terraform.tfstate` in private source control commit the
   newly modified `terraform.tfstate`

### Rebuild a single server

1. Find resource name
    - `terraform show`
    - ex: `aws_instance.web`
2. Taint the resource
    - `terraform taint aws_instance.web`
    - this will only mark the server for recreation
3. Capture the plan
    - `terraform plan`
    - this should show only the deletion of the instance and perhaps the
    modification of attached resources (eg: Elastic IP (eip), Elastic Block
    Storage (ebs)) that rely on the instance id
4. Apply the plan
    - `terraform apply`
    - this is the step that actually destroys the server and creates a new instance
5. Commit the results (only if you are tracking `terraform.tfstate` in private
   source control)
    - `git add terraform.tfstate*`
    - `git commit -m "[APPLY] - success rebuilding server aws_instance.web"`
6. Remove stale host key
    - `ssh-keygen -f "~/.ssh/known_hosts" -R OLD_IP_ADDRESS`
7. Test ssh
    - `ssh -i ~/.ssh/picoCTF_production_rsa admin@NEW_IP_ADDRESS`
8. Re-provision/Configure
    - run the relevant ansible playbooks

### Other Notes
- Error waiting for Volume (vol-XYZABC) to detach from Instance
    - This is caused when an instance with an attached volume attempts to mutate
    - Use `terrafrom taint aws_instance.XXX` to cause a full deletion and recreation
    - Check with `terraform plan` then if it makes sense apply with `terraform apply` 

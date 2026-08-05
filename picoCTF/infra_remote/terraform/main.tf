# Terraform configuration to deploy picoCTF to AWS (production)

###
# This configuration instantiates a single tier infrastructure for running the
# picoCTF platform on AWS. Once deployed this infrastructure can be
# provisioned, configured, and administered with ansible.
#
# You should not need to make any changes to this file (for the default setup),
# make all edits in variables.tf
###

terraform {
  required_version = ">= 0.12"
}

# AWS Specific config (single region)
# Configured to get access_key and secret_key from a shared credentials file
# For additional methods: https://www.terraform.io/docs/providers/aws/
provider "aws" {
  region  = local.region
  profile = local.profile
  shared_credentials_file = local.shared_credentials_file
}


###
# Infrastructure Components:
# The following sections use the specified variables to create the resources
# necessary to run the picoCTF platform in a single tier environment.
###

# Add SSH key which will be inserted as authorized in each machine
resource "aws_key_pair" "auth" {
    key_name   = local.key_name
    public_key = file(local.public_key_path)
}


###
# Network configuration:
# This is a simple network configuration where all machines are on a virtual network
# that is attached via an gateway to the internet. All machines placed in this subnet
# receive a public IP address
###

# Create a VPC (network) to launch our instances into
resource "aws_vpc" "network" {
    cidr_block = local.vpc_cidr
    tags       = local.default_tags
}

# Create an internet gateway to give our subnet access to the outside world
resource "aws_internet_gateway" "network" {
    vpc_id = aws_vpc.network.id
    tags   = local.default_tags
}

# Grant the VPC internet access on its main route table
resource "aws_route" "internet_access" {
    route_table_id         = aws_vpc.network.main_route_table_id
    destination_cidr_block = "0.0.0.0/0"
    gateway_id             = aws_internet_gateway.network.id
}

# Create a public facing subnet to launch our instances into
# Maps public IP automatically so every instance gets a public IP
# Security Groups are then used to restrict access
resource "aws_subnet" "public" {
    vpc_id                  = aws_vpc.network.id
    cidr_block              = local.public_subnet_cidr
    availability_zone       = local.az
    map_public_ip_on_launch = true
    tags                    = local.default_tags
}


###
# Server Instance Configuration:
# There are two primary servers necessary to run picoCTF (web, shell). This is
# the same configuration used in the default development setup.
###

resource "aws_instance" "web" {

    # AWS machine settings
    ami               = data.aws_ami.ubuntu.id
    instance_type     = local.web_instance_type
    availability_zone = local.az

    # Network settings
    vpc_security_group_ids = [aws_security_group.web.id]
    subnet_id              = aws_subnet.public.id
    private_ip             = local.web_private_ip
  
    # metadata
    key_name = aws_key_pair.auth.id
    tags     = merge(local.default_tags, map("Name", local.web_name))
}

resource "aws_instance" "shell" {

    # AWS machine settings
    ami               = data.aws_ami.ubuntu.id
    instance_type     = local.shell_instance_type
    availability_zone = local.az

    # Network settings
    vpc_security_group_ids = [aws_security_group.shell.id]
    subnet_id              = aws_subnet.public.id
    private_ip             = local.shell_private_ip

    # metadata
    key_name = aws_key_pair.auth.id
    tags     = merge(local.default_tags, map("Name", local.shell_name))
}


###
# Elastic IP:
# This simplifies configuration and administration by allowing us to rebuild
# and recreate the servers while maintaining the same public IP.
###

# Create Elastic IP for web server
resource "aws_eip" "web" {
    instance = aws_instance.web.id
    vpc      = true
    tags     = merge(local.default_tags, map("Name", local.web_name))
}

# Create Elastic IP for shell server
resource "aws_eip" "shell" {
    instance = aws_instance.shell.id
    vpc      = true
    tags     = merge(local.default_tags, map("Name", local.shell_name))
}


###
# Elastic Block Storage:
# This allows competition data such as the database and user home directories
# to be easily backed up, restored, and moved to new machines. This increases
# flexibility to easily scale.
###

# Create EBS volume for MongoDB data and journal
# having them on the same device allows backup with --journal
resource "aws_ebs_volume" "db_data_journal" {
    availability_zone = local.az
    size              = local.db_ebs_data_size
    tags              = merge(local.default_tags, map("Name", local.db_name))
}

# Attach data and journal volume to the instance running the database
resource "aws_volume_attachment" "db_data_journal" {
  device_name  = local.db_ebs_data_device_name
  volume_id    = aws_ebs_volume.db_data_journal.id
  instance_id  = aws_instance.web.id
  force_detach = true
}


###
# Output:
# Return the following to the user for configuring the ansible inventory
###

output "Web_Elastic_IP_address" {
  value = aws_eip.web.public_ip

}

output "Shell_Elastic_IP_address" {
  value = aws_eip.shell.public_ip
}

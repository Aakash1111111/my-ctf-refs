# Variables used to configure a production deployment

###
# Input Variables:
# Edit the values in this section to customize your deployment.
###

locals {

  # CTF: if you make a copy of this configuration be sure to change this
  # value so that your infrastructures are distinct
  ctf = "picoCTF"

  # AWS Settings: choose best for where your CTF is
  region                  = "us-east-1"
  profile                 = "picoCTF"
  shared_credentials_file = "~/.aws/credentials"

  # SSH Settings: local path to key that will be authorized on the machines
  public_key_path = "~/.ssh/picoCTF_production_rsa.pub"

  # Machine Instance Type
  web_instance_type   = "t2.micro"
  shell_instance_type = "t2.micro"
}

###
# Default Variables:
# The following values are reasonable and should not need to be changed.
##

locals {
  # Name for AWS to track SSH key by.
  key_name = local.ctf

  # selected automatically from available zones
  az = "${data.aws_availability_zones.available.names[0]}"

  # Network settings for Virtual Private Cloud
  vpc_cidr           = "10.0.0.0/16"
  public_subnet_cidr = "10.0.1.0/24"

  # Internal IP address for the servers
  web_private_ip   = "10.0.1.10"
  shell_private_ip = "10.0.1.20"

  # EBS Volumes: NOTE changing the instance type may require changing the device_name
  db_ebs_data_size        = "10"
  db_ebs_data_device_name = "/dev/xvdf"

  # Tags that allow visibility via AWS Consolse
  default_tags = {
    Environment = "production"
    Group       = "picoCTF"
    Event       = local.ctf
  }

  # Additional name tags which will be added to relevant resources
  web_name   = "picoCTF-web"
  shell_name = "picoCTF-shell"
  db_name    = "picoCTF-db"

}

###
# Data Sources:
# These are automatic data sources which will pull valid values directly from
# AWS with no additional configuration required.
###

data "aws_availability_zones" "available" {}

data "aws_ami" "ubuntu" {
  most_recent = true

  # pinned to a specific release to prevent drift
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-20200430"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  owners = ["099720109477"] # Canonical
}


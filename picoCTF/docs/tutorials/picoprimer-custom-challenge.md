Welcome to the PicoPrimer page on adding a "trivial" custom challenge. By trivial, we mean as simple as possible - which is good for demonstrating the moving parts of the picoCTF platform.

This primer is intended to be used as a checklist with hyperlinks to other pages that can guide or step you through solving each bulleted item. We try to assume very little about your current set up or knowledge of picoCTF.

1. Install the picoCTF platform's required software:
   1. Install Vagrant (which is for creating Virtual Machines - commonly VM's - via terminal command): [Vagrant by HashiCorp](https://www.vagrantup.com/)
   1. Install virtualization software (Vagrant needs this): There are multiple options, but [VirtualBox](https://www.virtualbox.org/) will work
1. Set up the picoCTF platform: [This repo's root README has the best instructions for this](https://github.com/picoCTF/picoCTF#quick-start)
1. _Sanity Check; you should have evidence of the following after completing the previous step:_
   * _Two (2) Virtual Machines:_
      * _Web Server: reachable via browsers by the following URL `http://192.168.2.2`_
      _* Shell Server: reachable via `ssh` at IP address `192.168.2.3`_
   _* Credentials for the Site Administrator account (this is the first user one registers on the Web Server via a browser)_
1. SSH to Shell Server as vagrant user: `$ ssh vagrant@192.168.2.3`
1. ltj:the rest of the lines are WIP, but a good outline: Create a simple challenge: [Walkthrough on creating a buffer overflow challenge](./buffer-overflow-challenge-beginner.md)
1. Use `shell_manager` to deploy your new challenge: [Overview of testing, packaging, installing, deploying, and enabling challenges](../adding-your-own-content.md#testing-your-problem)
1. Test as a non-privileged participant!

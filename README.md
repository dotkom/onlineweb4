Onlineweb 4
==========

[![Build Status](https://online.ntnu.no/tc/app/rest/builds/buildType%3A%28Onlineweb4_Build%29/statusIcon)](https://online.ntnu.no/tc/viewType.html?buildTypeId=Onlineweb4_Build)

Requirements
------------

Versions are of time of writing (11.10.2013)

* [VirtualBox (4.2.18)](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant (v1.3.4)](http://downloads.vagrantup.com/)
* [Git](http://git-scm.com)
 * the [GitHub for Windows](http://windows.github.com/) app is probably the easiest way to install and use git on windows
* SSH - On Windows ssh is included with git/github for windows.

Installation
------------

# git and repository setup
```bash
$ git config --global core.autocrlf false
$ git config --global user.name "<your github username>"
$ git config --global user.email <your.github@email.com>
$ git clone --recursive git@github.com:dotKom/onlineweb4.git
$ cd onlineweb4
```

Alternatively on windows, use the github for windows app to setup everything


# vagrant

This will create a virtual machine with all that is required to start developing

* see the Vagrantfile for special vm configuration options and
* see the vagrantbootstrap.sh script for provisioning options

```bash
$ vagrant up
```

If anything goes wrong
```bash
$ vagrant reload # will re-up the machine without destroying it
$ vagrant destroy -f # delete everything to start from scratch
$ vagrant provision # re-run the provisioning (vagrantbootstrap.sh) task
```

After the machine is up and provisioned you can ssh to the instance to run a server
```bash
$ vagrant ssh # if prompted for a password just type 'vagrant'
$ workon onlineweb # this is the virtualenv
$ cd /vagrant # this is the mounted shared folder of the project root
$ python manage.py runserver 0.0.0.0:8000 # this will bind to all interfaces on port 8000 (forwarded as 8001)
```

Site should be available at http://localhost:8001

To suspend/resume the vm
```bash
$ vagrant suspend onlineweb
$ vagrant resume onlineweb
```

# vagrant for parallels
If you wish to use a parallels, the Vagrantfile has been set up to accept that. There is one more step to setup this.
```bash
$ vagrant plugin install vagrant-parallels
```

Then run `vagrant up` with parallels as the provider.
```bash
$ vagrant up --provider=parallels
```

Some things are worth noting here;  
CONS:
* The port forwarding doesn't work for parallels, as of the time of writing this (26.11.13).
* You have to access the dev server on <parallels-ip>:<some port> instead of the neat localhost:8001 that virtualbox let's you do.

PROS:
* Parallels is _much_ better than virtualbox for mac. 
* VB will hang after sleep, which requires a shutdown of the machine to keep working, causing lots of .swp files. This has never happened to me (melwil) with parallels.
* Parallels is faster, tab completion, checking out branches, stashing, is all ~instant in parallels, while it can take as much as seconds in VB.
* Parallels was made for Mac.

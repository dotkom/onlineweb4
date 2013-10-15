Onlineweb 4
==========

Requirements
------------

versions are of time of writing (11.10.2013)

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

alternatively on windows, use the github for windows app to setup everything


# vagrant

this will create a virtual machine with all that is required to start developing

* see the Vagrantfile for special vm configuration options and
* see the vagrantbootstrap.sh script for provisioning options

```bash
$ vagrant up
```

if anything goes wrong
```bash
$ vagrant reload # will re-up the machine without destroying it
$ vagrant destroy -f # delete everything to start from scratch
$ vagrant provision # re-run the provisioning (vagrantbootstrap.sh) task
```

after the machine is up and provisioned you can ssh to the instance to run a server
```bash
$ vagrant ssh # if prompted for a password just type 'vagrant'
$ workon onlineweb # this is the virtualenv
$ cd /vagrant # this is the mounted shared folder of the project root
$ python manage.py runserver 0.0.0.0:8000 # this will bind to all interfaces on port 8000 (forwarded as 8001)
```

site should be available at http://localhost:8001

to suspend/resume the vm
```bash
$ vagrant suspend onlineweb
$ vagrant resume onlineweb
```
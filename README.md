Onlineweb 4
==========
[![Build Status](https://ci.online.ntnu.no/api/badges/dotKom/onlineweb4/status.svg)](https://ci.online.ntnu.no/dotKom/onlineweb4) [![codecov](https://codecov.io/gh/dotKom/onlineweb4/branch/develop/graph/badge.svg)](https://codecov.io/gh/dotKom/onlineweb4)


Requirements
------------

Download the latest versions of the following software

* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/downloads.html)
* [Git](http://git-scm.com)
    * the [GitHub for Windows](http://windows.github.com/) app is probably the easiest way to install and use Git on Windows
* SSH - On Windows SSH is included with Git/GitHub for Windows.

Installation
------------

# Git and repository setup
```bash
$ git config --global core.autocrlf false
$ git config --global user.name "<your github username>"
$ git config --global user.email <your.github@email.com>
$ git clone --recursive git@github.com:dotKom/onlineweb4.git
$ cd onlineweb4
```


CD/CI
=======

Pushes made to the develop branch will trigger a redeployment of the application on [dev.online.ntnu.no](https://dev.online.ntnu.no).

Pull requests trigger containerized builds that perform code style checks and tests. You can view the details of these tests by clicking the "detail" link in the pull request checks status area.

aefaef

Alternatively on Windows, use the GitHub for Windows app to setup everything

Docker
======

We're using Docker and docker-compose for the development environment. Run `docker-compose pull` followed by `docker-compose build` to get your services up and ready, then start OW4 using `docker-compose up -d` (`-d` for "detached" mode). This will expose the Django development webserver on `http://localhost:8000`. For more information, check out `docker-compose.yml`. For logs when using detached mode, run `docker-compose logs` (or `docker-compose logs <service>` for logs for a specific service).

The Docker setup can be streamlined by some simple make commands. Executing `make` will run `docker-compose pull`, `docker-compose build` and finally `docker-compose up -d` -- a simple way to build a new version of the project and get it up and running (note: this does not actually fetch the latest changes from GitHub!). For simply running OW4 using make, execute `make run`. These commands execute `docker-compose up -d`, which runs docker-compose in detached mode. To check the logs from Docker, check out `make logs` or `docker-compose logs` as described earlier.

To find out if the container is running or not, execute `make status`. This will list currently running containers and their status.

Vagrant
=======

This will create a virtual machine with all that is required to start developing

* see the Vagrantfile for special VM configuration options and
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

After the machine is up and provisioned you can SSH to the instance to run a server
```bash
$ vagrant ssh # if prompted for a password just type 'vagrant'
$ workon onlineweb # this is the virtualenv
$ cd /vagrant # this is the mounted shared folder of the project root
$ python manage.py runserver 0.0.0.0:8000 # this will bind to all interfaces on port 8000 (forwarded as 8001)
```

Site should be available at http://localhost:8001

To suspend/resume the VM
```bash
$ vagrant suspend onlineweb
$ vagrant resume onlineweb
```

Vagrant for Parallels
=====================

If you wish to use a Parallels, the Vagrantfile has been set up to accept that. There is one more step to setup this.
```bash
$ vagrant plugin install vagrant-parallels
```

Then run `vagrant up` with parallels as the provider.
```bash
$ vagrant up --provider=parallels
```

Some things are worth noting here;  
CONS:
* The port forwarding doesn't work for Parallels, as of the time of writing this (26.11.13).
* You have to access the dev server on <parallels-ip>:<some port> instead of the neat localhost:8001 that virtualbox let's you do.

PROS:
* Parallels is _much_ better than virtualbox for mac. 
* VB will hang after sleep, which requires a shutdown of the machine to keep working, causing lots of .swp files. This has never happened to me (melwil) with Parallels.
* Parallels is faster, tab completion, checking out branches, stashing, is all ~instant in Parallels, while it can take as much as seconds in VB.
* Parallels was made for Mac.

# Onlineweb 4
[![Build Status](https://ci.online.ntnu.no/api/badges/dotkom/onlineweb4/status.svg?branch=develop)](https://ci.online.ntnu.no/dotkom/onlineweb4) [![codecov](https://codecov.io/gh/dotKom/onlineweb4/branch/develop/graph/badge.svg)](https://codecov.io/gh/dotKom/onlineweb4)

## Frameworks

### Frontend

The frontend code is located in the `assets` folder.  
It's a mixture of old jQuery code and newer React code.  
The code is built with [webpack](http://webpack.js.org/) and transpiled using [Babel](https://babeljs.io/).

*Some static files are still stored in `files/static`, but should be moved to `assets` and included using webpack*.

### Backend
 
Python 3 with [Django](https://docs.djangoproject.com/) is used as a backend and is mostly located in the `apps` folder.  
Django templates are in `templates` folder.  
The API uses [Django REST framework](http://www.django-rest-framework.org/) 


## Installation - Git and repository setup

```bash
$ git config --global core.autocrlf false
$ git config --global user.name "<your github username>"
$ git config --global user.email your.github@email.com
$ git clone git@github.com:dotkom/onlineweb4.git
$ cd onlineweb4
```

## Development environment

The easiest way to get started with development is to use the provided Docker images.  
On the other hand on slower machines Docker might be noticeable slower in which case a local installation using virtualenv can be preferred. 

### Docker and Docker Compose

To fire up the dev environment, you should use [docker-compose](https://docs.docker.com/compose/overview/).

Install it by running `pip install docker-compose`.

There exists a `Makefile` in the project root directory. This simplifies interaction with docker and docker-compose.

Simply run `make` to build and start onlineweb4, and run `make stop` to stop it.

To view output from onlineweb4, run `make logs`. To view output from a specific service (e.g. django), prepend the `make` command with `OW4_MAKE_TARGET=django`.

If you can't use `make`, you can fire up the dev environment by issuing `docker-compose up -d`.

If the site doesn't load properly the first time you are running the project, you might need to restart Docker once by running `docker-compose restart`.

### Local installation

A few packages are required to build our Python depedencies: 

- libjpeg-dev
- ghostscript

If these aren't already installed pip will likely fail to build the packages.

If you are oldschool and like using python virtual envs, just activate your env,
run `pip install -r requirements.txt`, then `python manage.py migrate`, before starting the dev server with `python manage.py runserver`.

Next, you need to fire up the front-end stuff, by running `npm install` followed by `npm start`.

The project should now be available at [http://localhost:8000](http://localhost:8000)

## CD/CI

Pushes made to the develop branch will trigger a redeployment of the application on [dev.online.ntnu.no](https://dev.online.ntnu.no).

Pull requests trigger containerized builds that perform code style checks and tests. You can view the details of these tests by clicking the "detail" link in the pull request checks status area.

# Onlineweb 4
[![Build Status](https://ci.online.ntnu.no/api/badges/dotkom/onlineweb4/status.svg?branch=develop)](https://ci.online.ntnu.no/dotkom/onlineweb4) [![codecov](https://codecov.io/gh/dotKom/onlineweb4/branch/develop/graph/badge.svg)](https://codecov.io/gh/dotKom/onlineweb4) [![Requirements Status](https://requires.io/github/dotkom/onlineweb4/requirements.svg?branch=develop)](https://requires.io/github/dotkom/onlineweb4/requirements/?branch=develop) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


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
### Setting up your Git user and cloning the repo
```bash
$ git config --global core.autocrlf false
$ git config --global user.name "<your github username>"
$ git config --global user.email your.github@email.com
$ git clone git@github.com:dotkom/onlineweb4.git
$ cd onlineweb4
```
### Setting up the onlineweb4
Download dependencies by running
```bash
make
```

Let's apply all the django changes to the database by running
```bash
# creates migrations by packaging model changes into individual migration files
make makemigrations

# applies the migrations/changes to your database
make migrate
```

Last but not least, let's create a superuser, a user with all types of permissions.
```bash
# bash into the docker container
make bash-backend

# create a super user from inside the container
python manage.py createsuperuser
```
Now follow the instructions by typing a name, password and an email.

## Development environment

The easiest way to get started with development is to use the provided Docker images.  
On the other hand on slower machines Docker might be noticeable slower in which case a local installation using virtualenv can be preferred. 

### Docker and Docker Compose

To fire up the dev environment, you should use [Docker](https://docs.docker.com/install/). Following that, you will need [docker-compose](https://docs.docker.com/compose/overview/), which can be installed following [this](https://docs.docker.com/compose/install/) guide.

There is a `Makefile` located in the root directory. This can be used to manage the application without direct interaction with `docker`, `docker-compose`, et al.

Simply run `make` to build and start onlineweb4, and run `make stop` to stop it.

To view output from onlineweb4, run `make logs`. To view output from a specific service (e.g. django), prepend the `make` command with `OW4_MAKE_TARGET=django`.

If you can't use `make`, you can fire up the dev environment by issuing `docker-compose up -d`.

If the site doesn't load properly the first time you are running the project, you might need to restart Docker once by running `docker-compose restart`.

Remember to run `make migrate` your first time, and after migrations have been made.

#### Alternative to Docker: Local installation

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

## Tools

Builds will fail if our requirements for code style are not met. To ensure that you adhere to our code guidelines, we recommend you run linting tools locally before pushing your code. This can be done by running `make lint`, and you can automatically fix the backend linting by running `make lint-backend-fix`. Running `make test` will run our tests and linters all at once. Look to our [Makefile](https://github.com/dotkom/onlineweb4/blob/86ef0e267bdad3346a705551d2a3d377b2802d81/Makefile#L55) for more specific commands.

Running `make test` frequently can be quite inefficient, which is why we recommend using editors that support linting your code as you go. For JavaScript, we use [ESLint](https://eslint.org/docs/about/), with editor plugins available [here](https://eslint.org/docs/user-guide/integrations). Correspondingly, we use [stylelint](https://stylelint.io) for our stylesheets, with editor plugins available [here](https://github.com/stylelint/stylelint/blob/master/docs/user-guide/complementary-tools.md#editor-plugins). For Python, we use [Black](https://black.readthedocs.io/en/stable/), [isort](https://github.com/timothycrosley/isort) and [Flake8](http://flake8.pycqa.org/). We highly recommend setting up your editor to automatically fix linting issues, which can be done for [Black](https://black.readthedocs.io/en/stable/editor_integration.html), and [isort](https://github.com/timothycrosley/isort/wiki/isort-Plugins)

### Our recommendation

In dotkom, we find that [PyCharm](https://www.jetbrains.com/pycharm/) is a great IDE that is well suited for contributing to onlineweb4. It'll come with support for ESLint, stylelint, and PEP 8 out of the box, and can be set up to run isort and Flake8 with some ease. We recommend it to our beginners who don't want to spend a lot of time setting up the plugins or extensions mentioned above, or don't have any preferences of their own yet. You can apply for a free student license [here](https://www.jetbrains.com/student/).

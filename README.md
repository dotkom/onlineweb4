# Onlineweb 4
[![Build Status](https://cloud.drone.io/api/badges/dotkom/onlineweb4/status.svg)](https://cloud.drone.io/dotkom/onlineweb4)  [![codecov](https://codecov.io/gh/dotkom/onlineweb4/branch/main/graph/badge.svg)](https://codecov.io/gh/dotkom/onlineweb4) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) [![Total alerts](https://img.shields.io/lgtm/alerts/g/dotkom/onlineweb4.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/dotkom/onlineweb4/alerts/) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/dotkom/onlineweb4.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/dotkom/onlineweb4/context:python) 


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
git config core.autocrlf false
git config user.name "<your github username>"
git config user.email your.github@email.com
git clone git@github.com:dotkom/onlineweb4.git
cd onlineweb4
```

## Development environment

The easiest way to get started with development is to use the provided Docker images.
On the other hand on slower machines Docker might be noticeable slower in which case a local installation using virtualenv can be preferred.

### Docker and Docker Compose

To fire up the dev environment, you should use [Docker](https://docs.docker.com/install/). Following that, you will need [docker-compose](https://docs.docker.com/compose/overview/), which can be installed following [this](https://docs.docker.com/compose/install/) guide.

There is a `Makefile` located in the root directory. This can be used to manage the application without direct interaction with `docker`, `docker-compose`, et al.

If you can't use `make`, you can fire up the dev environment by issuing `docker-compose up -d`.

If the site doesn't load properly the first time you are running the project, you might need to restart Docker once by running `docker-compose restart`.

#### Alternative to Docker: Local installation

A few packages are required to build our Python depedencies:

- libjpeg-dev
- ghostscript

If these aren't already installed poetry will likely fail to build the packages.

Onlineweb4 is setup to use the [Poetry](https://python-poetry.org/) for dependency mangement.

To install dependencies run `poetry install`. If you're system doesn't have a compatible version of python, 3.7.x, 
you can use pyenv.

To start the server firstly run the database migrations with `python manage.py migrate`, and run the server with `python manage.py runserver`.

Next, you need to fire up the front-end stuff, by running `npm install` followed by `npm start`.

The project should now be available at [http://localhost:8000](http://localhost:8000)

### Setting up Onlineweb4 with Docker and Docker-compose

After installing Docker and docker-compose, Download dependencies by running
```bash
make build
```

You also need to set up the database, by running
```bash
# Enter the bash-terminal in the Docker container
make bash-backend

# Run the migrations
python manage.py migrate
```
For your convenience, you can also just run `make migrate`

To exit the Docker bash-terminal, use `^D` (`ctrl + D`) or `exit`

And to be able to log in, you should create a superuser, a user with all types of permissions by default.
```bash
# If you aren't already in the bash-terminal in Docker
make bash-backend

# Create a super user from inside the container
python manage.py createsuperuser
```
Now follow the instructions by supplying a name, password and an email.

You can then start Onlineweb4 by running

```bash
make start
```

And your local version of Onlineweb4 should be available on [http://localhost:8000](http://localhost:8000)!
You can stop it with `make stop`

To view output from onlineweb4, run `make logs`. To view output from a specific service (e.g. django), use one of the following:
```bash
OW4_MAKE_TARGET=django make logs # for django
OW4_MAKE_TARGET=webpack make logs # for the frontend
```

#### Creating migrations

After doing changes to a model, you will need to make an migration for the database-scheme.
You can automatically create those commands by running the following:

```bash
make makemigrations
```

Note: we run format-linting on our migration files. Luckily we have set up the `make makemigrations` command to also 
automatically format the created files. So if you use our command you should not need to do anything more. If you 
are oldschool and prefer running `./manage.py makemigrations` yourself, then you will need to either run `black`
afterwards, or run `make lint-backend-fix` after creating the migrations, so that they are properly formatted. You
could also look at the [Makefile](./Makefile) to see how we redirect the output if you want to do so yourself.

## Continuous Integration and Continuous Delivery

Pushes made to the `main` branch will trigger a redeployment of the application on [dev.online.ntnu.no](https://dev.online.ntnu.no).

Pull requests trigger containerized builds that perform code style checks and tests. 
You can view the details of these tests by clicking the "detail" link in the pull request checks status area.

> **Important:** We have integration tests with Stripe that require valid test-API-keys, those tests are **not**
> run by default locally, or when creating a PR from a fork of this repository.

## Tools

Builds will fail if our requirements for code style are not met. To ensure that you adhere to our code guidelines, we recommend you run linting tools locally before pushing your code. This can be done by running `make lint`, and you can automatically fix the backend linting by running `make lint-backend-fix`. Running `make test` will run our tests and linters all at once. Look to our [Makefile](https://github.com/dotkom/onlineweb4/blob/86ef0e267bdad3346a705551d2a3d377b2802d81/Makefile#L55) for more specific commands.

Running `make test` frequently can be quite inefficient, which is why we recommend using editors that support linting your code as you go. For JavaScript, we use [ESLint](https://eslint.org/docs/about/), with editor plugins available [here](https://eslint.org/docs/user-guide/integrations). Correspondingly, we use [stylelint](https://stylelint.io) for our stylesheets, with editor plugins available [here](https://github.com/stylelint/stylelint/blob/master/docs/user-guide/complementary-tools.md#editor-plugins). For Python, we use [Black](https://black.readthedocs.io/en/stable/), [isort](https://github.com/timothycrosley/isort) and [Flake8](http://flake8.pycqa.org/).
We highly recommend setting up your editor to automatically fix linting issues, which can be done for [Black](https://black.readthedocs.io/en/stable/editor_integration.html), and [isort](https://github.com/timothycrosley/isort/wiki/isort-Plugins)

### Our recommendation

In dotkom, we find that [PyCharm](https://www.jetbrains.com/pycharm/) is a great IDE that is well suited for contributing to onlineweb4. It'll come with support for ESLint, stylelint, and PEP 8 out of the box, and can be set up to run isort and Flake8 with some ease. We recommend it to our beginners who don't want to spend a lot of time setting up the plugins or extensions mentioned above, or don't have any preferences of their own yet. You can apply for a free student license [here](https://www.jetbrains.com/student/).

## API  
Onlineweb4 comes with an API located at `/api/v1`.  
Autogenerated Swagger-docs can be found at `/api/v1/docs`.  
Some endpoints require user authentication. See [OAuth/OIDC](#oauthoidc).  

## OAuth/OIDC  
Onlineweb4 has an Oauth2/OIDC-provider built-in, allowing external projects to authenticate users through Onlineweb4.  
[Auth0: Which flow should I use?](https://auth0.com/docs/authorization/which-oauth-2-0-flow-should-i-use)  
[Digital Ocean: Introduction to Oauth 2](https://www.digitalocean.com/community/tutorials/an-introduction-to-oauth-2)  
[Auth0: Authorization Flow with PKCE - Single Page Apps](https://auth0.com/docs/flows/authorization-code-flow-with-proof-key-for-code-exchange-pkce)  


### For production setup  
To authenticate users through `https://online.ntnu.no`, contact `dotkom@online.ntnu.no` for issuing a new client.  
Follow the steps in _Usage in a project_ for how to use the client information.

### For local setup
Initialize OpenID Connect by creating an RSA-key:
```bash
docker-compose run --rm django python manage.py creatersakey
```  

go to `localhost:8000/admin` and log in with your administrator user.  
Scroll to `OpenID Connect Provider` and add a new `Client`.  
Fill in the information related to the selected flow (see linked documentation on flows).
Upon saving, a client-ID and client secret is generated for you. Revisit the client you created to retrieve the id and secret.  

### Usage in a project  
[Automated configuration and all endpoints](https://online.ntnu.no/openid/.well-known/openid-configuration)  
There are many packages that provide oauth2/oidc-helpers. These can be quite helpful to automate much of the OAuth2-flow.
If you have configured your client correctly, the following `cURL`-commands are the equivalent of the authorization code flow and illustrate how the HTTP-requests are setup.  

```bash
curl -v http://{url:port}/openid/authorize?\
  client_id={your client_id}&\
  redirect_uri={your configured callback url}&\
  response_type={your configured response type}&\
  scope={your configured scopes}&\
  state={persistant state through the calls}&\
```  
  
_Note:_ Two common scopes are `openid` and `onlineweb4`
This will trigger a 302 Redirect where the user will be asked to login to Onlineweb4.  
Upon successfull login, the user are redirect to your configured callback url with `?code={authorization_code}&state{persistant state}` added to the url.  
Retrieve the code from the URL (and check that the state has not been tampered with, i.e. still is the same one.)  
Exchange the code for an access token which will be used to identify the user in your application.  

```bash
curl -v http://{url:port}/openid/token?
  \grant_type={grant, i.e. the content of the parenthesis of the response type}
  \code={code from previous step}
```

This response will contain some basic information about the user, based on which scopes you requested, as well as an access token which can be added to the authorization header to request data from the API.  
To use the access token, add `Authorization: Bearer {token}` to your requests to the API.

As a last step, basic user information can be retrieved from the endpoint `/openid/userinfo`.  
This endpoint requires the `Authorization`-header to be set as mentioned above and the `profile`-scope to have been requested.  
More information, such as `email` can be retrieved if the `email`-scope have been requested.  
The full set of scopes for userinfo are: [email, address, phone, offline_access].  
More information about this endpoint can be found in the [spec](https://openid.net/specs/openid-connect-basic-1_0-28.html#userinfo)  

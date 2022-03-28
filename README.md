# Onlineweb 4

[![Build Status](https://cloud.drone.io/api/badges/dotkom/onlineweb4/status.svg)](https://cloud.drone.io/dotkom/onlineweb4) [![codecov](https://codecov.io/gh/dotkom/onlineweb4/branch/main/graph/badge.svg)](https://codecov.io/gh/dotkom/onlineweb4) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) [![Total alerts](https://img.shields.io/lgtm/alerts/g/dotkom/onlineweb4.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/dotkom/onlineweb4/alerts/) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/dotkom/onlineweb4.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/dotkom/onlineweb4/context:python)

## Frameworks

### Zappa

The project is deployed to AWS Lambda with the use of [Zappa](https://github.com/zappa/zappa). To
deploy (should be done automatically), build a Docker image with Dockerfile.zappa and push it to AWS ECR.
Then you can run `zappa update <stage> -d <docker-ecr-image>`. You'll have also have to build NPM and deploy static first if this has been changed since last deploy.

#### Example for prod

```bash
VERSION=4.X.X
STAGE=Production
zappa save-python-settings-file $STAGE

docker build . --build-arg VERSION=$VERSION -t onlineweb4-zappa:latest -t 891459268445.dkr.ecr.eu-north-1.amazonaws.com/onlineweb4-zappa:$VERSION

docker push 891459268445.dkr.ecr.eu-north-1.amazonaws.com/onlineweb4-zappa:$VERSION

zappa update $STAGE -d 891459268445.dkr.ecr.eu-north-1.amazonaws.com/onlineweb4-zappa:$VERSION
```

### Frontend

The frontend code is located in the `assets` folder.
It's a mixture of old jQuery code and newer React code.
The code is built with [webpack](http://webpack.js.org/) and transpiled using [Babel](https://babeljs.io/).

### Backend

Python 3 with [Django](https://docs.djangoproject.com/) is used as a backend and is mostly located in the `apps` folder.
Django templates are in `templates` folder.
The API uses [Django REST framework](http://www.django-rest-framework.org/)

To find the list of available commands when using `python manage.py` (alternatively `./manage.py`), see the
[docs](https://docs.djangoproject.com/en/3.2/ref/django-admin/).

## Installation - Git and repository setup

### Setting up your Git user and cloning the repo

```shell
git config core.autocrlf false
git config user.name "<your github username>"
git config user.email your.github@email.com
git clone git@github.com:dotkom/onlineweb4.git
cd onlineweb4
```

Alternatively we also recommend using GitHub's own [Command Line Interface (CLI)](https://cli.github.com), which
also eases the creation of pull requests with `gh pr create`.

## Development environment

The by far easiest way to start developing is to use Visual Studio Code (VS Code) with
[remote-containers](https://code.visualstudio.com/docs/remote/containers).
The development environment should be pre-built as part of our Gtihub Actions workflows,
and should work automatically upon opening this repo locally in VS Code with the extension installed.

Note: the setup has a focus on the Djangp-backend, the frontend is likely to require more manual intervention,
if you need help feel free to reach out to someone in Dotkom for help!

### Devcontainer variants

We have two ways to run the development environment, with the one suiting you depending on how you want
to interact with the project dependencies:

#### Pre-built image with included dependencies (default)

Uses the imge built automatically on change to dependencies, can be quite big, and has a very long wait-time.
Not recommended if you want to actively develop with changing dependencies.

You can build this image locally by adding `"docker-compose.build.yml"` to the end of the
`dockerComposeFile`-array in [`devcontainer.json`](/.devcontainer/devcontainer.json).
Will be very slow if you frequently change dependencies.

#### Pre-built image without included dependencies

Useful if your development often involves changing dependencies in `poetry`, but requires that you manually run
`yarn install` and `poetry install`.
You can use this method by adding `"docker-compose.no-deps.yml"` to the end of the
`dockerComposeFile`-array in [`devcontainer.json`](/.devcontainer/devcontainer.json).

You can also build the image locally instead of using our pre-built version by using `docker-compose.no-deps-build.yml` instead.

### Local installation

The performance of the containers might be a little lackluster on macOS, in which case you can
attempt to set up a local Python environemnt. Onlineweb4 is setup to use
[Poetry](https://python-poetry.org/) for dependency mangement.

The following commands _should_ make `py.test` work out of the box, if they do not please open an issue.

```shell
# static files are required for tests to pass
# we use Node 16 and Yarn v1, see e.g. https://github.com/nvm-sh/nvm
# for help with managing multiple Node versions on your system
yarn install --frozen-lockfile
yarn build:test

# recommended for easier debugging
# saves the virtual environment and all packages to `.venv`
poetry config virtualenvs.in-project true

# if you do not have Python 3.9 installed, or Python3.10, you can use e.g. pyenv to manage them.
poetry install

# use the virtual environment
poetry shell

py.test
```

To start the server first run the database migrations with `python manage.py migrate`,
and run the server with `python manage.py runserver`.

Next, you need to fire up the front-end stuff, by running `npm install` followed by `npm start`.

The project should now be available at [http://localhost:8000](http://localhost:8000)

### Testing and linting

We use [pre-commit](https://pre-commit.com) to run linting before each commit.
`pre-commit` should be automaticall available after running `poetry install`,
you can set up the git-hooks locally:

```shell
pre-commit install
# or if you have not activated the Poetry environment
poetry run pre-commit install
```

And run the lints manually by running

```shell
pre-commit run --all-files
```

To run the tests you can call

```shell
# first run either this or build:prod
# most tests using Django templates require the `webpack-stats*.json` to exists
npm run build:test

py.test
```

Which should work as long as you have properly set up the Python environment.

For linting and testing the frontend, we have the following commands, which are not currently set
up with `pre-commit`:

```shell
npm run lint
npm run test
```

#### Code Test Coverage


```shell
# you can then open the report in a browser, or instead generate XML-report and use any tool to view it.
py.test --cov= --cov-report html
```

#### Editor integration

CI will fail if our requirements for code style are not met. To ensure that you adhere to our code guidelines, we recommend you run linting tools locally before pushing your code. This can be done automatically by using the above-mentioned `pre-commit`.

For potentially improved productivity, you can integrate the linting and formatting tools we use in your editor:

- [Black](https://black.readthedocs.io/en/stable/)
- [isort](https://github.com/timothycrosley/isort)
- [Flake8](http://flake8.pycqa.org/).
- [ESLint](https://eslint.org/docs/about/), with editor plugins available [here](https://eslint.org/docs/user-guide/integrations).
- [stylelint](https://stylelint.io) for our stylesheets, with editor plugins available [here](https://github.com/stylelint/stylelint/blob/master/docs/user-guide/complementary-tools.md#editor-plugins).

### Creating migrations

After doing changes to a model, you will need to make an migration for the database-scheme.
You can automatically create those commands by running the following:

```shell
python manage.py makemigrations
```

Note that migrations should be properly formatted and linted as other files, but should be fixed with our
pre-commit hooks.

## Continuous Integration and Continuous Delivery

Pushes made to the `main` branch will trigger a redeployment of the application on [dev.online.ntnu.no](https://dev.online.ntnu.no).

Pull requests trigger containerized builds that perform code style checks and tests.
You can view the details of these tests by clicking the "detail" link in the pull request checks status area.

> **Important:** We have integration tests with Stripe that require valid test-API-keys, those tests are **not**
> run by default locally, or when creating a PR from a fork of this repository. To run them, first get ahold of
> the appropriate testing keys, then add them to an `.env` file in the project root,
> the name of the environment variables are in
> [`.devcontainer/devcontainer.env`](.devcontainer/devcontainer.env).

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

```shell
python manage.py creatersakey
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

```shell
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

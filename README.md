# Onlineweb 4

[![codecov](https://codecov.io/gh/dotkom/onlineweb4/branch/main/graph/badge.svg)](https://codecov.io/gh/dotkom/onlineweb4)
[![Open in Remote - Containers](https://img.shields.io/static/v1?label=Remote%20-%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/dotkom/onlineweb4)

To run OnlineWeb4 you need two things:

1. [`node`](https://nodejs.org/en/download/package-manager) >= 20 to install and bundle the frontend assets
2. [`uv`](https://docs.astral.sh/uv/) to install python dependencies.

You can replace `uv` for a version of Python 3.13, but that requires managing your Python version yourself, and `uv` helps sync and isolate your Python dependencies, and is wicked fast.

```sh
# install node + uv from above

uv sync
# activate Python environment
source ./.venv/bin/activate

npm ci
npm run build

./manage.py migrate

./manage.py runserver

# OnlineWeb4 should be available on localhost:8000

# run tests
pytest

# install pre-commit hooks to automatically check formatting
pre-commit install
```

## Authentication

Authentication goes through our Auth0-tenant, to get access to development configuration contact dotkom@online.ntnu.no.

If you are a member of dotkom you can use our configuration in doppler. 

```sh
doppler setup
doppler run -- ./manage.py runserver
```

## Frameworks

### Frontend

Frontend code is located in the `assets` folder. It's a mixture of old jQuery code and newer React code.
The code is bundled with [esbuild](https://esbuild.github.io).

### Backend

Python 3 with [Django](https://docs.djangoproject.com/) is used as a backend and is mostly located in the `apps` folder.
Django templates are in `templates` folder.
The API uses [Django REST framework](http://www.django-rest-framework.org/)

To find the list of available commands when using `python manage.py` (alternatively `./manage.py`), see the
[docs](https://docs.djangoproject.com/en/5.0/ref/django-admin/).

## Installation - Git and repository setup

### Setting up your Git user and cloning the repo

We recommend using GitHub's own [Command Line Interface (CLI)](https://cli.github.com):

```shell
gh auth login
gh repo clone dotkom/onlineweb4
cd onlineweb4
```

Normal flow for making a PR:

```sh
git switch -c new-feature
# exciting code
pytest
# can use `git add -ip`
git add <files>
git commit
gh pr create
```

### Testing and linting

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.
To run the linting run

```sh
ruff check .
```

You can add git hooks that automatically check the linting when committing with `pre-commit install`.

```shell
pre-commit install
```

And run the lints manually by running

```shell
pre-commit run --all-files
```

To run the tests you can call

```shell
# most tests using Django templates require the `webpack-stats.json` to exists
npm run build

pytest
```

Which should work as long as you have properly set up the Python environment.

### Creating migrations

After doing changes to a model, you will need to make an migration for the database-scheme.
You can automatically create those commands by running the following:

```shell
./manage.py makemigrations
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

### Manual release

### Zappa

The project is deployed to AWS Lambda with the use of [Zappa](https://github.com/zappa/zappa). To
deploy (should be done automatically), build a Docker image and push it to AWS ECR.
Then you can run `zappa update <stage> -d <docker-ecr-image>`. You'll have also have to build NPM and deploy static first if this has been changed since last deploy.

#### Example for prod

```shell
# create git tag / github release with release notes first
# if this is prod add `-prod` suffix
VERSION=4.X.X-prod
# OR VERSION=4.X.X if dev
STAGE=prod
REGION=eu-north-1
# log in to AWS in some way first https://docs.aws.amazon.com/cli/latest/userguide/getting-started-prereqs.html#getting-started-prereqs-keys
# jq is just to extract the "Account" json-key automatically
AWS_ACCOUNT_ID=$(aws sts get-caller-identity | jq .Account)
DOCKER_REGISTRY=$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
TAG=$DOCKER_REGISTRY/onlineweb4-zappa:$VERSION
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $DOCKER_REGISTRY

# If zappa is not available you must install it, alternatively use devcontainer:
uv sync --extra prod
source ./.venv/bin/activate

zappa save-python-settings-file $STAGE

docker build . --build-arg VERSION=$VERSION -t $IMAGE --no-cache
docker push $TAG
zappa update $STAGE -d $TAG

# If you also have changed static files you must run the following:
docker build . --target=static-files -t ow4-static
ID=$(docker create ow4-static)
docker cp $ID:/srv/app/static static
BUCKET_NAME=$( yq ".${STAGE}.environment_variables.OW4_S3_BUCKET_NAME" zappa_settings.yml )
aws s3 sync static "s3://${BUCKET_NAME}/static" --delete --acl=public-read
```

## API

Onlineweb4 comes with an API located at `/api/v1`.  
Autogenerated Swagger-docs can be found at `/api/schema/swagger-ui`.  

### Running without `uv`

```sh
# must print >= 3.13
python --version

# create a python virtual environment
python -m vevnv .venv
source ./.venv/bin/activate

pip install .

./manage.py runserver

# dev-dependencies like pytest have not been installed, so can't run test
```

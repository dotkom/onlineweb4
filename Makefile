.PHONY: all bash-backend build clean down logs restart shell start status stop \
	drone lint-only test-only lint-backend lint-frontend test-backend test-frontend

DOCKER_COMPOSE_FILE = ./docker/docker-compose.yml
DOCKER_COMPOSE_COMMAND = @docker-compose -f ./docker/docker-compose.yml
BACKEND_SERVICE_NAME = django
BACKEND_LINT_FOLDERS = apps scripts utils
BACKEND_TEST_FOLDERS ?= apps

FRONTEND_SERVICE_NAME = webpack

all: down build start

bash-backend:
	$(DOCKER_COMPOSE_COMMAND) run --rm $(BACKEND_SERVICE_NAME) bash

build:
	$(DOCKER_COMPOSE_COMMAND) build

clean: down
	$(DOCKER_COMPOSE_COMMAND) rm --force
	$(DOCKER_COMPOSE_COMMAND) prune --force

down:
	$(DOCKER_COMPOSE_COMMAND) down --volumes

logs:
	$(DOCKER_COMPOSE_COMMAND) logs -f $(OW4_MAKE_TARGET)

migrate:
	$(DOCKER_COMPOSE_COMMAND) --rm $(BACKEND_SERVICE_NAME) python manage.py migrate

# Reasoning for having two makemigrations:
# the migration-files that Django output are not formatted according to Black code-style
# there is no plan to add that as a feature to Django ref. https://code.djangoproject.com/ticket/24275
# therefore we have modified the default one to also format _only_ the files that Django created
# which is why we copy the output of the interactive `makemigrations`-command into a temporary file
# and then search for the lines containing the paths to the migrations, and send them to Black with xargs
# we also set the `pipefail` option, because we want the command to fail if makemigrations fails
makemigrations-no-format:
	$(DOCKER_COMPOSE_COMMAND) --rm $(BACKEND_SERVICE_NAME) python manage.py makemigrations $(OW4_MAKE_TARGET)

makemigrations:
	$(DOCKER_COMPOSE_COMMAND) --rm $(BACKEND_SERVICE_NAME) bash -c "set -o pipefail \
&& python manage.py makemigrations $(OW4_MAKE_TARGET) 2>&1 \
| tee /tmp/created_migrations.log \
&& grep '^[ \t]*apps/' /tmp/created_migrations.log \
| xargs black"

restart: stop start

shell:
	$(DOCKER_COMPOSE_COMMAND) --rm $(BACKEND_SERVICE_NAME) python manage.py shell

start:
	$(DOCKER_COMPOSE_COMMAND) up -d
	@echo "Onlineweb4 is running in a detached container."
	@echo "To view output from onlineweb4, run make logs. To view output from a specific service (e.g. django), prepend the make command with OW4_MAKE_TARGET=django."

status:
	$(DOCKER_COMPOSE_COMMAND) ps

stop:
	$(DOCKER_COMPOSE_COMMAND) stop

tail:
	$(DOCKER_COMPOSE_COMMAND) logs $(OW4_MAKE_TARGET)

# Testing tools

test: lint-only test-only

lint-only: lint-backend lint-frontend
test-only: test-backend test-frontend

lint-backend:
	$(DOCKER_COMPOSE_COMMAND) run --rm $(BACKEND_SERVICE_NAME) tox --recreate -e flake8 -e isort -e black

lint-frontend:
	$(DOCKER_COMPOSE_COMMAND) run --rm $(FRONTEND_SERVICE_NAME) npm run lint

lint-backend-fix:
	$(DOCKER_COMPOSE_COMMAND) run --rm $(BACKEND_SERVICE_NAME) bash -c "isort apps scripts utils && black apps scripts utils onlineweb4"

test-backend:
	$(DOCKER_COMPOSE_COMMAND) run --rm $(BACKEND_SERVICE_NAME) py.test $(BACKEND_TEST_FOLDERS) -n auto

test-frontend:
	$(DOCKER_COMPOSE_COMMAND) run --rm $(FRONTEND_SERVICE_NAME) npm run test


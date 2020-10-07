.PHONY: all bash-backend build clean docs down logs restart shell start status stop \
	drone lint-only test-only lint-backend lint-frontend test-backend test-frontend

BACKEND_SERVICE_NAME = django
BACKEND_LINT_FOLDERS = apps middleware scripts utils
BACKEND_TEST_FOLDERS = apps

FRONTEND_SERVICE_NAME = webpack

all: down build start

bash-backend:
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) bash

build:
	@docker-compose build

clean: down
	@docker-compose rm --force
	@docker volume prune --force

docs:
	cd docs; make html

down:
	@docker-compose down --volumes

logs:
	@docker-compose logs -f $(OW4_MAKE_TARGET)

migrate:
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) python manage.py migrate

# Reasoning for having two makemigrations:
# the migration-files that Django output are not formatted according to Black code-style
# there is no plan to add that as a feature to Django ref. https://code.djangoproject.com/ticket/24275
# therefore we have modified the default one to also format _only_ the files that Django created
# which is why we copy the output of the interactive `makemigrations`-command into a temporary file
# and then search for the lines containing the paths to the migrations, and send them to Black with xargs
makemigrations-no-format:
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) python manage.py makemigrations $(OW4_MAKE_TARGET)

makemigrations:
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) bash -c "python manage.py makemigrations $(OW4_MAKE_TARGET) 2>&1 | tee /tmp/created_migrations.log && grep '^[ \t]*apps/' /tmp/created_migrations.log | xargs black"

restart: stop start

shell:
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) python manage.py shell

start:
	@docker-compose up -d
	@echo "Onlineweb4 is running in a detached container."
	@echo "To view output from onlineweb4, run make logs. To view output from a specific service (e.g. django), prepend the make command with OW4_MAKE_TARGET=django."

status:
	@docker-compose ps

stop:
	@docker-compose stop

tail:
	@docker-compose logs $(OW4_MAKE_TARGET)

# Testing tools

drone:
	@drone exec

test: lint-only test-only

lint-only: lint-backend lint-frontend
test-only: test-backend test-frontend

lint-backend:
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) tox --recreate -e flake8 -e isort -e black

lint-frontend:
	@docker-compose run --rm $(FRONTEND_SERVICE_NAME) npm run lint

lint-backend-fix:
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) bash -c "isort apps middleware scripts utils && black apps middleware scripts utils onlineweb4"

test-backend:
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) py.test $(BACKEND_TEST_FOLDERS)

test-frontend:
	@docker-compose run --rm $(FRONTEND_SERVICE_NAME) npm run test


.PHONY: all bash-backend build clean down logs restart shell start status stop \
	drone lint-only test-only lint-backend lint-frontend test-backend test-frontend

BACKEND_SERVICE_NAME = django
BACKEND_LINT_FOLDERS = apps middleware scripts utils
BACKEND_TEST_FOLDERS = apps

FRONTEND_SERVICE_NAME = webpack

all: build start

bash-backend:
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) bash

build:
	@docker-compose build
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) python webpack_resolve.py

clean: stop
	@docker-compose rm --force

down:
	@docker-compose down

logs:
	@docker-compose logs -f $(OW4_MAKE_TARGET)

migrate:
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) python manage.py migrate

makemigrations:
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) python manage.py makemigrations $(OW4_MAKE_TARGET)

restart: stop start

shell:
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) python manage.py shell

start:
	@docker-compose up -d

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
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) flake8 $(BACKEND_LINT_FOLDERS)
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) isort -c -rc $(BACKEND_LINT_FOLDERS)

lint-frontend:
	@docker-compose run --rm $(FRONTEND_SERVICE_NAME) npm run lint

test-backend:
	@docker-compose run --rm $(BACKEND_SERVICE_NAME) py.test $(BACKEND_TEST_FOLDERS)

test-frontend:
	@docker-compose run --rm $(FRONTEND_SERVICE_NAME) npm run test


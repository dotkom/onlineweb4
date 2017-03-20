.PHONY: build up run logs start stop down rm status exec django manage

build:
	docker-compose pull
	docker-compose build

up:
	docker-compose up -d

run: up

logs:
	docker-compose logs

start:
	docker-compose start

stop:
	docker-compose stop

down:
	docker-compose down

rm:
	docker-compose rm

status:
	docker-compose ps

exec:
	docker-compose exec

django:
	docker-compose exec django

manage:
	docker-compose exec django python manage.py

default: build up

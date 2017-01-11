.PHONY: build up run logs start stop down rm status

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

default: build up

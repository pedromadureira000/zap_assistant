dev:
	@python manage.py runserver -v2

shell:
	@python manage.py shell_plus

docker-compose-up:
	@docker-compose -f docker-compose-dev.yml up

update:
	@git pull
	@docker-compose build app celery
	@docker-compose run app python manage.py migrate
	@docker-compose run app python manage.py collectstatic --noinput
	@docker-compose up -d --force-recreate --remove-orphans
	@docker system prune -f

autopep8:
	@find . -name "*py" | xargs autopep8 --in-place --aggressive --aggressive --max-line-length 100

.PHONY: postgres redis

postgres:
	@postgres -D ${POSTGRES_DATA_DIR} -k ${POSTGRES_SOCKET_DIR} -h 127.0.0.1 -d 2 -s

deploy:
	@git push heroku main --force

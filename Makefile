dev:
	@python manage.py runserver -v2

shell:
	@python manage.py shell_plus

uuid:
	@python -c 'import uuid; print(uuid.uuid4())'

.PHONY: postgres redis

```bash
git clone git@github.com:pedromadureira000/ai_experiment.git
cd ai_experiment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-test.txt
cp contrib/env-sample .env
psql postgres://username:pass@localhost:5432/postgres
postgres=# create database ai_experiment;
postgres=# \q
python manage.py migrate
python manage.py createsuperuser
```

## Running celery
```
celery -A ai_experiment worker -l INFO --pool=gevent --concurrency=8 --hostname=worker -E
```

## Header Authentication
* For clients to authenticate, the token key should be included in the Authorization HTTP header. The key should be prefixed by the string literal "Token", with whitespace separating the two strings. For example:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## Get Auth Token

```
curl -X POST -d '
    {
        "whatsapp": "556299999999",
        "password": "pass"
    }
    ' -H "Content-Type: application/json;" http://127.0.0.1:8000/user/gettoken
```

## Authenticated API calls
curl -X POST -d '{}' -H "Authorization: Token <your-token>" -H "Content-Type: application/json" http://127.0.0.1:8000/api_path

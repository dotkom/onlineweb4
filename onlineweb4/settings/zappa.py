### Using https://github.com/hashicorp/vault-lambda-extension
### Loads secrets from vault
import json

secrets_dir = "/tmp/secrets"

db_creds_file = open(f"{secrets_dir}/db.json")
env_file = open(f"{secrets_dir}/env.json")

db_creds = json.load(db_creds_file)["data"]
env = json.load(env_file)["data"]["data"]

print(db_creds)
DATABASES = {
    'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'ow4dev',
            'USER': db_creds["username"],
            'PASSWORD': db_creds["password"],
            'HOST': env["OW4_POSTGRES_HOST"],
            'PORT': '5432',
    },
}

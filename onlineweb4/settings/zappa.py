# Using https://github.com/hashicorp/vault-lambda-extension
# Loads secrets from vault
import json

from decouple import config

DEBUG = False
TEMPLATE_DEBUG = False

secrets_dir = "/tmp/secrets"

db_creds_file = open(f"{secrets_dir}/db.json")
env_file = open(f"{secrets_dir}/env.json")

db_creds = json.load(db_creds_file)["data"]
env = json.load(env_file)["data"]["data"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config("OW4_DATABASE_NAME", default="ow4dev"),
        "USER": db_creds["username"],
        "PASSWORD": db_creds["password"],
        "HOST": env["POSTGRES_HOST"],
        "PORT": "5432",
    },
}

SECRET_KEY = env["SECRET_KEY"]

DATAPORTEN = {
    "STUDY": {
        "ENABLED": config("OW4_DP_STUDY_ENABLED", cast=bool, default=False),
        "TESTING": config("OW4_DP_STUDY_TESTING", cast=bool, default=True),
        "CLIENT_ID": env["DP_STUDY_CLIENT_ID"],
        "CLIENT_SECRET": env["DP_STUDY_CLIENT_SECRET"],
        "REDIRECT_URI": config("OW4_DP_STUDY_REDIRECT_URI", default=""),
        "PROVIDER_URL": "https://auth.dataporten.no/oauth/token",
        "SCOPES": ["openid", "userid-feide", "profile", "groups", "email"],
    }
}

VIMEO_API_TOKEN = env["VIMEO_API_TOKEN"]

WEB_PUSH_PRIVATE_KEY = env["WEB_PUSH_PRIVATE_KEY"]

RECAPTCHA_PUBLIC_KEY = env["RECAPTCHA_PUBLIC_KEY"]
RECAPTCHA_PRIVATE_KEY = env["RECAPTCHA_PRIVATE_KEY"]
NOCAPTCHA = True
RECAPTCHA_USE_SSL = True

STRIPE_PUBLIC_KEYS = {
    "arrkom": env["STRIPE_PUBKEY_ARRKOM"],
    "prokom": env["STRIPE_PUBKEY_PROKOM"],
    "trikom": env["STRIPE_PUBKEY_TRIKOM"],
    "fagkom": env["STRIPE_PUBKEY_FAGKOM"],
}

STRIPE_PRIVATE_KEYS = {
    "arrkom": env["STRIPE_PRIVKEY_ARRKOM"],
    "prokom": env["STRIPE_PRIVKEY_PROKOM"],
    "trikom": env["STRIPE_PRIVKEY_TRIKOM"],
    "fagkom": env["STRIPE_PRIVKEY_FAGKOM"],
}

SLACK_INVITER = {"team_name": "onlinentnu", "token": env["SLACK_TOKEN"]}

APPROVAL_SETTINGS = {
    "SEND_APPLICANT_NOTIFICATION_EMAIL": True,
    "SEND_APPROVER_NOTIFICATION_EMAIL": True,
}

AWS_SES_REGION_NAME = "eu-north-1"
AWS_SES_REGION_ENDPOINT = f"email.{AWS_SES_REGION_NAME}.amazonaws.com"
SESSION_COOKIE_SAMESITE = None
ADMINS = (("dotKom", "utvikling@online.ntnu.no"),)


# Override "spam-settings" for django-wiki
WIKI_REVISIONS_PER_HOUR = 1000
WIKI_REVISIONS_PER_MINUTES = 500
WIKI_ATTACHMENTS_EXTENSIONS = [
    "pdf",
    "doc",
    "odt",
    "docx",
    "txt",
    "xlsx",
    "xls",
    "png",
    "psd",
    "ai",
    "ods",
    "zip",
    "jpg",
    "jpeg",
    "gif",
    "patch",
]

WIKI_MARKDOWN_HTML_WHITELIST = [
    "br",
    "hr",
]

BEDKOM_GROUP_ID = 3
FAGKOM_GROUP_ID = 6
COMMON_GROUP_ID = 17

WIKI_OPEN_EDIT_ACCESS = [
    12,  # Komiteer
    14,  # Eldstesaadet
]
WIKI_OPEN_EDIT_ACCESS_GROUP_ID = 22

GROUP_SYNCER = [
    {
        "name": "Komite-enkeltgrupper til gruppen Komiteer",
        "source": [
            1,  # arrKom
            2,  # banKom
            3,  # bedKom
            4,  # dotKom
            5,  # eksKom
            6,  # fagKom
            7,  # proKom
            8,  # triKom
            33,  # Realfagskjelleren
            18,  # seniorKom
            10,  # pangKom
            11,  # Hovedstyret
            16,  # appKom
            9,  # velKom
            24,  # itex
            36,  # Online IL
        ],
        "destination": [12],  # Komiteer
    },
    {
        "name": "bedKom og fagKom til felles gruppe (bed&fagKom)",
        "source": [3, 6],  # bedKom  # fagKom
        "destination": [17],  # bed&fagKom
    },
    {
        "name": "Komiteer som kan redigere Online public wiki",
        "source": [12, 14],  # Komiteer  # Eldsteraadet
        "destination": [22],  # Wiki - Online edit permissions
    },
    {
        "name": "Komiteer som kan redigere Online Komiteer wiki",
        "source": [12, 18],  # Komiteer  # SeniorKom
        "destination": [23],  # Wiki - Komiteer access permissions
    },
    {
        "name": "Buddyssystemet for tilgang til wiki",
        "source": [
            27,  # Riddere
            18,  # Seniorkom
            31,  # Ex-Hovedstyre
            11,  # Hovedstyret
        ],
        "destination": [30],  # Buddy
    },
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

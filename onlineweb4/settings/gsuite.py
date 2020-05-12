import os

from decouple import config

from .base import PROJECT_ROOT_DIRECTORY

OW4_GSUITE_SETTINGS = {
    "CREDENTIALS": {
        "type": config("OW4_GSUITE_ACCOUNT_TYPE", default="service_account"),
        "project_id": config("OW4_GSUITE_PROJECT_ID", default=""),
        "private_key_id": config("OW4_GSUITE_PRIVATE_KEY_ID", default=""),
        "private_key": config("OW4_GSUITE_PRIVATE_KEY", default=""),
        "client_email": config("OW4_GSUITE_CLIENT_EMAIL", default=""),
        "client_id": config("OW4_GSUITE_CLIENT_ID", default=""),
        "auth_uri": config("OW4_GSUITE_AUTH_URI", default=""),
        "token_uri": config("OW4_GSUITE_TOKEN_URI", default=""),
        "auth_provider_x509_cert_url": config("OW4_GSUITE_PROVIDER_CERT_URL", default=""),
        "client_x509_cert_url": config("OW4_GSUITE_CLIENT_CERT_URL", default=""),
    },
    "DOMAIN": config("OW4_GSUITE_SYNC_DOMAIN", default="online.ntnu.no"),
    # DELEGATED_ACCOUNT: G Suite Account with proper permissions to perform insertions and removals.
    "DELEGATED_ACCOUNT": config("OW4_GSUITE_DELEGATED_ACCOUNT", default=""),
    "ENABLED": config("OW4_GSUITE_ENABLED", cast=bool, default=False),
}

OW4_GSUITE_ACCOUNTS = {
    "ENABLED": config("OW4_GSUITE_ACCOUNTS_ENABLED", cast=bool, default=False),
    "ENABLE_INSERT": config(
        "OW4_GSUITE_ACCOUNTS_ENABLE_INSERT", cast=bool, default=False
    ),
}

OW4_GSUITE_SYNC = {
    "CREDENTIALS": OW4_GSUITE_SETTINGS.get("CREDENTIALS"),
    "DOMAIN": OW4_GSUITE_SETTINGS.get("DOMAIN"),
    "DELEGATED_ACCOUNT": OW4_GSUITE_SETTINGS.get("DELEGATED_ACCOUNT"),
    "ENABLED": config("OW4_GSUITE_SYNC_ENABLED", cast=bool, default=False),
    "ENABLE_INSERT": config("OW4_GSUITE_SYNC_ENABLE_INSERT", cast=bool, default=False),
    "ENABLE_DELETE": config("OW4_GSUITE_SYNC_ENABLE_DELETE", cast=bool, default=False),
    # OW4 name (lowercase) -> G Suite name (lowercase)
    "GROUPS": {
        "appkom": "appkom",
        "arrkom": "arrkom",
        "bankom": "bankom",
        "bedkom": "bedkom",
        "dotkom": "dotkom",
        "ekskom": "ekskom",
        "fagkom": "fagkom",
        "fond": "fond",
        "hovedstyret": "hovedstyret",
        "jubkom": "jubkom",
        "prokom": "prokom",
        "seniorkom": "seniorkom",
        "trikom": "trikom",
        "tillitsvalgte": "tillitsvalgte",
        "redaksjonen": "redaksjonen",
        "ekskom": "ekskom",
        "itex": "itex",
        "velkom": "velkom",
        "interessegrupper": "interessegrupper",
        "online-il": "online-il",
        "techtalks": "techtalks",
        "komiteledere": "komiteledere",
    },
}

MAILING_LIST_USER_FIELDS_TO_LIST_NAME = {"infomail": "info", "jobmail": "oppdrag"}

from decouple import config

WEB_PUSH_PRIVATE_KEY = config("OW4_VAPID_PRIVATE_KEY", default="")
WEB_PUSH_ENABLED = config("OW4_WEB_PUSH_ENABLED", default=False, cast=bool)

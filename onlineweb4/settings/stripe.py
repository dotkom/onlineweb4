from decouple import config


# Online stripe keys.
# For development replace with https://online.ntnu.no/wiki/komiteer/dotkom/aktuelt/onlineweb4/keys/
# For production login to Stripe
STRIPE_PUBLIC_KEYS = {
    "arrkom": config("OW4_DJANGO_STRIPE_PUBLIC_KEY_ARRKOM", default="pk_test_replace_this"),
    "prokom": config("OW4_DJANGO_STRIPE_PUBLIC_KEY_PROKOM", default="pk_test_replace_this"),
    "trikom": config("OW4_DJANGO_STRIPE_PUBLIC_KEY_TRIKOM", default="pk_test_replace_this"),
}

STRIPE_PRIVATE_KEYS = {
    "arrkom": config("OW4_DJANGO_STRIPE_PRIVATE_KEY_ARRKOM", default="pk_test_replace_this"),
    "prokom": config("OW4_DJANGO_STRIPE_PRIVATE_KEY_PROKOM", default="pk_test_replace_this"),
    "trikom": config("OW4_DJANGO_STRIPE_PRIVATE_KEY_TRIKOM", default="pk_test_replace_this"),
}
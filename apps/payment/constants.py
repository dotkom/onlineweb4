class StripeKey:
    # Stripe keys are configured in "onlineweb4/settings/stripe.py"
    ARRKOM = 'arrkom'
    PROKOM = 'prokom'
    TRIKOM = 'trikom'
    FAGKOM = 'fagkom'

    ALL_TYPES = (ARRKOM, PROKOM, TRIKOM, FAGKOM,)
    ALL_CHOICES = [(t, t) for t in ALL_TYPES]


class TransactionType:
    KIOSK = 'kiosk'
    WEB_SHOP = 'webshop'
    EVENT = 'event'

    ALL_TYPES = (KIOSK, WEB_SHOP, EVENT,)
    ALL_CHOICES = [(t, t) for t in ALL_TYPES]

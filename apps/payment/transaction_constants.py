class TransactionSource:
    STRIPE = "stripe"
    CASH = "cash"
    SHOP = "shop"
    TRANSFER = "transfer"

    ALL_CHOICES = (
        (STRIPE, "Stripe"),
        (CASH, "Kontant"),
        (SHOP, "Kiosk"),
        (TRANSFER, "Overføring"),
    )

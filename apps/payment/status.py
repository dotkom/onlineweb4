"""
Handling orders from Stripe results in needed to keep track of the status of the charge/intent.
The status of a payment follows the following lifecycle.
"""

"""
When a payment has been intended, but not yet completed.
In some cases this case can be skipped. Stripe charges/intents can be successful on first try.
"""
PENDING = 'pending'
"""
When a payment has succeeded in Stripe. At this point the payment should be inserted into out database.
When the payment is set as SUCCEEDED, we should immediately try to set it to DONE.
"""
SUCCEEDED = 'succeeded'
"""
When the payment has been stored, and the corresponding change has been made in our database.
"""
DONE = 'done'
"""
When the payment has been refunded to the card holder by Stripe.
Changes made when completing the charge (when going from SUCCEEDED to DONE) should be undone in this case.
"""
REFUNDED = 'refunded'
""" When the payment is no longer relevant, and all side effects have been removed """
REMOVED = 'removed'

PAYMENT_STATUSES = [
    PENDING,
    SUCCEEDED,
    DONE,
    REFUNDED,
    REMOVED,
]

PAYMENT_STATUS_CHOICES = [(status, status) for status in PAYMENT_STATUSES]

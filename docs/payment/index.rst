Payment
=======

.. toctree::
   :maxdepth: 2
   
   api

Payment is implemented as a :class:`django.contrib.contenttypes.models.ContentType`

In theory it should be content type agnostic, but in reality the models are somewhat tightly coupled to the event system. 


Stripe
------

Instead of handling credit card info directly we let Stripe_ deal with that. 

.. _stripe.com: https://stripe.com/

Pay
***

*TODO*

Refunding
*********

*TODO*

Events
------

Some events cost money to attend and this is why the Payment application was originally created.

To enable the payment functionality on an Event a :class:`~apps.payment.models.Payment` object should be created. 
See :class:`~apps.payment.models.Payment` for documentation of the attributes required.

Attendance
**********

Depending on which :attr:`~apps.payment.models.Payment.payment_type` was selected three different things can happen.

- **Immediate**: Nothing? (Should be looked into)
- **Deadline**: Nothing? (Should be looked into)
- **Delay**: :class:`~apps.payment.models.PaymentDelay` is created using :attr:`~apps.payment.models.Payment.delay`.

Unattendance
************

If a user has already paid tey are not allowed to unattend events without being refunded first.
Otherwise any payment delays are just deleted if payment type is set to delay.


Waitlist bump
*************

Depending on which :attr:`~apps.payment.models.Payment.payment_type` was selected three different things can happen.

- **Immediate**: :class:`~apps.payment.models.PaymentDelay` is created with a delay of two days
- **Deadline**: :class:`~apps.payment.models.PaymentDelay` is created with a delay of :attr:`~apps.payment.models.Payment.deadline` or a minimum of two days.
- **Delay**: :class:`~apps.payment.models.PaymentDelay` is created using :attr:`~apps.payment.models.Payment.delay`.


Refund
******

If a user refund request passes the :meth:`~apps.payment.PaymentRelation.check_refund` check they are refunded using Stripe and then unattends the event like normal.

Mommy
*****

Like any good mom Mommy nags the event attendees for missing payments until the deadline has passed. 
Mommy starts sending reminder emails two days before the deadline.

If the deadline passes without a payment Mommy makes sure the users are punished by suspending them from any future events until they pay.

More specifically this happens:

- The user is sent an email notifying that the deadline has passed
- The organizing committee is notified by email too
- The user is assigned a mark
- The user is suspended until the payment is completed

:class:`~apps.payment.mommy.PaymentDelayHandler` handles payment type delay while
:class:`~apps.payment.mommy.PaymentReminder` handles deadlines.
Since some users may have custom payment delays these cases are also handled by :class:`~apps.payment.mommy.PaymentDelayHandler`
and ignored by :class:`~apps.payment.mommy.PaymentReminder`.

Webshop
-------

*TODO*

Nibble(Saldo)
-------------

*TODO*

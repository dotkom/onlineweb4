import locale
import logging

from django.core.mail import EmailMessage
from django.contrib.contenttypes.models import ContentType

from apps.payment.models import Payment, PaymentRelation
from apps.events.models import Event

class PaymenReminder(Task):

    @staticmethod
    def run():
        logger = logging.getLogger()
        logger.info("Event payment job started")
        locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

        event_payments = active_event_payments()

        today = timezone.now()

        for payment in event_payments:

            deadline_diff = (payment.deadline - today).days

            if deadline_diff <= 0:
                #TODO do stuff
            elif deadline_diff < 3:
                send_remainder_mail(payment)

    @staticmethod
    def active_event_payments():
        return Payment.objects.filter (instant_payment=False, active=True, content_type=ContentType.objects.get_for_model(Event))

    def send_remainder_mail(payment):
        #TODO
        subject = _(u"Betaling: ") + payment.content_object_description()
        message = _(u"Hei, du har ikke betalt for arrangement ") + payment.content_object_description()
        message += _(u"du må betale innen ") + payment.deadline
        message += _(u"Dersom du har spørsmål kan du sende mail til ") + payment.content_object_mail()
        message += _(u"\n\nMvh\nLinjeforeningen Online")

    def send_deadline_passed_mail(payment):
        subject = _(u"Betalingsfrist utgått: ") + payment.content_object_description()
        message = _(u"Hei, du har ikke betalt for arrangement ") + payment.content_object_description()
        message += _(u"fristen har utgått, og du får en prikk og 48 timer til å betale")
        message += _(u"Dersom du har spørsmål kan du sende mail til ") + payment.content_object_mail()
        message += _(u"\n\nMvh\nLinjeforeningen Online")

    def send_missed_payment_mail(payment):
        subject = _(u"Betalingsfrist utgått: ") + payment.content_object_description()
        message = _(u"Hei, du har ikke betalt for arrangement ") + payment.content_object_description()
        message += _(u"fristen har utgått, og du har mistet plassen din på arrangement")
        message += _(u"Dersom du har spørsmål kan du sende mail til ") + payment.content_object_mail()
        message += _(u"\n\nMvh\nLinjeforeningen Online")

schedule.register(PaymenReminder, day_of_week='mon-sun', hour=7, minute=05)

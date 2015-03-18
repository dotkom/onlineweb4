import locale
import logging

from django.core.mail import EmailMessage

from apps.payment.models import Payment, PaymentRelation

class PaymenReminder(Task):

    @staticmethod
    def run():
        logger = logging.getLogger()
        logger.info("Payment reminder job started")
        locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

        payment_events = active_payments()
        #payment_events = PaymentRelation.objects.filter(active=True)

        for payment in payment_events:
            

            if message.send:
                EmailMessage(message.subject, unicode(message), message.committee_mail, [], message.not_paid_mails).send()
                logger.info('Emails sent to: ' + str(message.not_paied_mails))
            else:
                logger.info("Everyone met. No mails sent to users")


    @staticmethod
    def generate_message ():

    @staticmethod
    def active_payments():
        return Payment.objects.filter (instanat_payment=True, payment__deadline__gt=timezone.now())

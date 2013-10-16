# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from django.core.mail import EmailMessage

from apps.feedback.models import FeedbackRelation
from apps.feedback.feedback_mails import FeedbackMail, Message

class Command(NoArgsCommand):
    help = "Loops trough active feedbacks and sends mails to attendees. Run it once a day"

    def handle_noargs(self, **options):
        
        active_feedbacks = FeedbackRelation.objects.filter(active=True)
       
        for feedback in active_feedbacks:
            message = FeedbackMail.generate_message(feedback)

            if message.send:
                EmailMessage(message.subject, unicode(message), message.committee_mail, [], message.attended_mails).send()

                if message.results_message:
                    EmailMessage("Feedback resultat", message.results_message,"online@online.ntnu.no", [message.committee_mail]).send()

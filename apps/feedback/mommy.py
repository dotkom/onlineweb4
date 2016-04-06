# -*- coding: utf-8 -*-

import locale
import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from apps.feedback.models import FeedbackRelation
from apps.marks.models import Mark, MarkUser
from apps.mommy import schedule
from apps.mommy.registry import Task


class FeedbackMail(Task):

    @staticmethod
    def run():
        logger = logging.getLogger("feedback")
        logger.info("Feedback job started")
        locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")
        active_feedbacks = FeedbackRelation.objects.filter(active=True)

        for feedback in active_feedbacks:
            message = FeedbackMail.generate_message(feedback, logger)
            logger.info("Status: " + message.status)

            if message.send:
                EmailMessage(
                    message.subject,
                    str(message),
                    message.committee_mail,
                    [],
                    message.attended_mails
                ).send()
                logger.info('Emails sent to: ' + str(message.attended_mails))

                if message.results_message:
                    EmailMessage(
                        "Feedback resultat",
                        message.results_message,
                        "online@online.ntnu.no",
                        [message.committee_mail]
                    ).send()
                    logger.info('Results mail sent to :' + message.committee_mail)

    @staticmethod
    def generate_message(feedback, logger):
        logger.info('Processing: "' + feedback.content_title() + '"')

        today = timezone.now().date()
        end_date = feedback.content_end_date()

        message = Message()

        if not end_date:
            message.status = "Content object has no date"
            return message

        # Return if the event has not yet happened
        if end_date.date() >= today:
            message.status = "Event not done"
            return message

        not_responded = FeedbackMail.get_users(feedback)
        logger.info('Not responded: ' + str(not_responded))

        # Return if everyone has answered
        if not not_responded:
            feedback.active = False
            feedback.save()
            message.status = 'Everyone has answered'
            return message

        message.attended_mails = FeedbackMail.get_user_mails(not_responded)

        message.committee_mail = FeedbackMail.get_committee_email(feedback)
        deadline = feedback.deadline.strftime("%d. %B")
        title = FeedbackMail.get_title(feedback)
        message.link = str("\n\n" + FeedbackMail.get_link(feedback))
        results_link = str(FeedbackMail.get_link(feedback) + "results")

        deadline_diff = (feedback.deadline - today).days

        message.subject = "Feedback: " + title
        message.intro = "Hei, vi ønsker tilbakemelding på \"" + title + "\""
        message.mark = FeedbackMail.mark_message(feedback)
        message.contact = "\n\nEventuelle spørsmål sendes til %s " % message.committee_mail
        message.date = FeedbackMail.date_message(end_date)

        if deadline_diff < 0:  # Deadline passed
            feedback.active = False
            feedback.save()
            logger.info("Deadline passed feedback set to inactive")
            message.status = "Deadine passed"

            if feedback.gives_mark:
                FeedbackMail.set_marks(title, not_responded)

                message.intro = "Fristen for å svare på \"%s\" har gått ut og du har fått en prikk." % title
                message.mark = ""
                message.date = ""
                message.link = ""
                message.send = True

            logger.info("Marks given to: " + str(not_responded))

        elif deadline_diff < 1:  # Last warning
            message.deadline = "\n\nI dag innen 23:59 er siste frist til å svare på skjemaet."

            message.results_message = "Hei, siste purremail på feedback skjema har blitt sendt til alle gjenværende " \
            "deltagere på \"{}\".\nDere kan se feedback-resultatene på:\n{}\n".format(title, results_link)
            message.send = True
            message.status = "Last warning"
        elif deadline_diff < 3 and feedback.gives_mark:  # 3 days from the deadline
            message.deadline = "\n\nFristen for å svare på skjema er %s innen kl 23:59." % deadline
            message.send = True
            message.status = "Warning message"
        elif not feedback.first_mail_sent:
            message.deadline = "\n\nFristen for å svare på skjema er %s innen kl 23:59." % deadline

            message.results_message = "Hei, nå har feedbackmail blitt sendt til alle deltagere på \"{}\"."
            "\nDere kan se resultatene på:\n{}\n".format(title, results_link)
            message.send = True
            message.status = "First message"

            feedback.first_mail_sent = True
            feedback.save()
            logger.info("first_mail_sent set")
        else:
            message.status = "No message generated"
        return message

    @staticmethod
    def end_date(feedback):
        end_date = feedback.content_end_date()

        if end_date:
            return end_date.date()
        else:
            return False

    @staticmethod
    def date_message(date):
        # If the object(event) doesnt have start date it will send
        # The first notification the day after the feedbackrelation is made
        if date:
            date_string = date.strftime("%d. %B")
            message_date = "som du var med på den %s:" % date_string
        else:
            message_date = ""

        return message_date

    @staticmethod
    def get_users(feedback):
        return feedback.not_answered()

    @staticmethod
    def get_user_mails(not_responded):
        return [user.email for user in not_responded]

    @staticmethod
    def get_link(feedback):
        return str(settings.BASE_URL + feedback.get_absolute_url())

    @staticmethod
    def get_title(feedback):
        return str(feedback.content_title())

    @staticmethod
    def get_committee_email(feedback):
        return feedback.content_email()

    @staticmethod
    def mark_message(feedback):
        if feedback.gives_mark:
            return "\nVær oppmerksom på at du får prikk dersom du ikke svarer " \
            "på disse spørsmålene innen fristen."
        else:
            return ""

    @staticmethod
    def set_marks(title, not_responded):
        mark = Mark()
        mark.title = "Manglende tilbakemelding på %s" % title
        mark.category = 4  # Missed feedback
        mark.description = "Du har fått en prikk fordi du ikke har levert tilbakemelding."
        mark.save()

        for user in not_responded:
            user_entry = MarkUser()
            user_entry.user = user
            user_entry.mark = mark
            user_entry.save()


class Message(object):
    subject = ""
    intro = ""
    date = ""
    deadline = ""
    mark = ""
    contact = ""
    link = ""
    send = False
    end = "\n\nMvh\nLinjeforeningen Online"
    results_message = False
    status = "-"

    committee_mail = ""
    attended_mails = False

    def __str__(self):
        message = "%s %s %s %s %s %s %s" % (
            self.intro,
            self.date,
            self.link,
            self.deadline,
            self.mark,
            self.contact,
            self.end
        )
        return message

schedule.register(FeedbackMail, day_of_week='mon-sun', hour=8, minute=00)

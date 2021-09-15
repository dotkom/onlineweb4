import locale
import logging

from celery.schedules import crontab
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from apps.feedback.models import FeedbackRelation
from apps.marks.models import Mark, MarkUser
from onlineweb4.celery import app


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **_kwargs):
    sender.add_periodic_task(
        crontab(hour=8, minute=0),
        event_feedback_handler.s(),
    )


@app.task
def event_feedback_handler():
    logger = logging.getLogger("feedback")
    logger.info("Feedback job started")
    locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")
    active_feedbacks = FeedbackRelation.objects.filter(active=True)

    for feedback in active_feedbacks:
        message = generate_message(feedback, logger)
        logger.info("Status: " + message.status)

        if message.send:
            EmailMessage(
                message.subject,
                str(message),
                message.committee_mail,
                [],
                message.attended_mails,
            ).send()
            logger.info(f"Emails sent to: {message.attended_mails}")

            if message.results_message:
                EmailMessage(
                    "Feedback resultat",
                    message.results_message,
                    "online@online.ntnu.no",
                    [message.committee_mail],
                ).send()
                logger.info(f"Results mail sent to :{message.committee_mail}")


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

    not_responded = feedback.not_answered()
    logger.info(f"Not responded: {not_responded}")

    # Return if everyone has answered
    if not not_responded:
        feedback.active = False
        feedback.save()
        message.status = "Everyone has answered"
        return message

    message.attended_mails = [user.email for user in not_responded]

    message.committee_mail = feedback.content_email()
    deadline = feedback.deadline.strftime("%d. %B")
    title = feedback.content_title()
    link = settings.BASE_URL + feedback.get_absolute_url()
    message.link = f"\n\n{link}"
    results_link = f"{link}results"

    deadline_diff = (feedback.deadline - today).days

    message.subject = f"Feedback: {title}"
    message.intro = f'Hei, vi ønsker tilbakemelding på "{title}"'
    message.mark = (
        (
            "\nVær oppmerksom på at du får prikk dersom du ikke svarer "
            "på disse spørsmålene innen fristen."
        )
        if feedback.gives_mark
        else ""
    )
    message.contact = f"\n\nEventuelle spørsmål sendes til {message.committee_mail} "
    # If the object(event) doesnt have start date it will send
    # The first notification the day after the feedbackrelation is made
    message.date = (
        f"som du var med på den {end_date.strftime('%d. %B')}:" if end_date else ""
    )

    if deadline_diff < 0:  # Deadline passed
        feedback.active = False
        feedback.save()
        logger.info("Deadline passed feedback set to inactive")
        message.status = "Deadine passed"

        if feedback.gives_mark:
            set_marks(title, not_responded)

            message.intro = (
                f'Fristen for å svare på "{title}" har gått ut og du har fått en prikk.'
            )
            message.mark = ""
            message.date = ""
            message.link = ""
            message.send = True

        logger.info(f"Marks given to: {not_responded}")

    elif deadline_diff < 1:  # Last warning
        message.deadline = (
            "\n\nI dag innen 23:59 er siste frist til å svare på skjemaet."
        )

        message.results_message = (
            f"Hei, siste purremail på feedback skjema har blitt sendt til alle gjenværende "
            f'deltagere på "{title}".\nDere kan se feedback-resultatene på:\n{results_link}\n'
        )
        message.send = True
        message.status = "Last warning"
    elif deadline_diff < 3 and feedback.gives_mark:  # 3 days from the deadline
        message.deadline = (
            f"\n\nFristen for å svare på skjema er {deadline} innen kl 23:59."
        )
        message.send = True
        message.status = "Warning message"
    elif not feedback.first_mail_sent:
        message.deadline = (
            f"\n\nFristen for å svare på skjema er {deadline} innen kl 23:59."
        )
        message.results_message = (
            f'Hei, nå har feedbackmail blitt sendt til alle deltagere på "{title}".'
            f"\nDere kan se resultatene på:\n{results_link}\n"
        )
        message.send = True
        message.status = "First message"

        feedback.first_mail_sent = True
        feedback.save()
        logger.info("first_mail_sent set")
    else:
        message.status = "No message generated"
    return message


def set_marks(title, not_responded):
    mark = Mark()
    mark.title = f"Manglende tilbakemelding på {title}"
    mark.category = 4  # Missed feedback
    mark.description = "Du har fått en prikk fordi du ikke har levert tilbakemelding."
    mark.save()

    for user in not_responded:
        user_entry = MarkUser()
        user_entry.user = user
        user_entry.mark = mark
        user_entry.save()


class Message:
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
        message = f"{self.intro} {self.date} {self.link} {self.deadline} {self.mark} {self.contact} {self.end}"
        return message

import logging

from django.core.mail import EmailMessage
from django.utils import timezone

from apps.events.models import AttendanceEvent
from apps.marks.models import Mark, sanction_users
from utils.email import AutoChunkedEmailMessage, handle_mail_error


def set_event_marks():
    logger = logging.getLogger()
    logger.info("Attendance mark setting started")

    # Gets all active attendance events thats suposed to give automatic marks
    attendance_events = active_events()

    for attendance_event in attendance_events:
        set_marks(attendance_event, logger)
        message = generate_message(attendance_event)

        if message.send:
            email = AutoChunkedEmailMessage(
                subject=message.subject,
                body=str(message),
                from_email=message.committee_mail,
                to=[],
                bcc=message.not_attended_mails,
            )
            email.send_in_background(
                error_callback=lambda e, nse, se, message=message: handle_mail_error(
                    e,
                    nse,
                    se,
                    to=[message.committee_mail],
                )
            )
            logger.info("Emails sent to: " + str(message.not_attended_mails))
        else:
            logger.info("Everyone met. No mails sent to users")

        if message.committee_message:
            EmailMessage(
                message.subject,
                message.committee_message,
                "online@online.ntnu.no",
                [message.committee_mail],
            ).send()
            logger.info("Email sent to: " + message.committee_mail)


def set_marks(attendance_event: AttendanceEvent, logger=None):
    if logger is None:
        logger = logging.getLogger()
    event = attendance_event.event
    logger.info('Proccessing "%s"', event.title)
    users = attendance_event.not_attended()
    mark_cause = Mark.Cause.NO_ATTENDANCE
    mark_weight = mark_cause.weight()

    if users:
        mark = Mark(
            title=f"Manglende oppmøte på {event.title}",
            cause=mark_cause,
            description=f"Du har fått {mark_weight} {'prikk' if mark_weight == 1 else 'prikker'} på grunn av manglende oppmøte på {event.title}.",
        )
        sanction_users(mark, users)

        for u in users:
            logger.info("%s marks given to: %s", mark_weight, u)

    attendance_event.marks_has_been_set = True
    attendance_event.save()


def generate_message(attendance_event):
    message = Message()

    not_attended = attendance_event.not_attended()
    event = attendance_event.event
    title = str(event.title)

    # return if everyone attended
    if not not_attended:
        return message

    message.not_attended_mails = [user.email for user in not_attended]

    message.committee_mail = event.feedback_mail()
    not_attended_string = "\n".join([user.get_full_name() for user in not_attended])
    mark_weight = Mark.Cause.NO_ATTENDANCE.weight()

    message.subject = title
    message.intro = f'Hei\n\nPå grunn av manglende oppmøte på "{title}" har du fått {mark_weight} {"prikk" if mark_weight == 1 else "prikker"}'
    message.contact = f"\n\nEventuelle spørsmål sendes til {message.committee_mail} "
    message.send = True
    message.committee_message = f'På grunn av manglende oppmøte på "{event.title}" har følgende brukere fått {mark_weight} {"prikk" if mark_weight == 1 else "prikker"}:\n'
    message.committee_message += not_attended_string
    return message


def active_events():
    return AttendanceEvent.objects.filter(
        automatically_set_marks=True,
        marks_has_been_set=False,
        event__event_end__lt=timezone.now(),
    )


class Message:
    subject = ""
    intro = ""
    contact = ""
    not_attended_mails = ""
    send = False
    end = "\n\nMvh\nLinjeforeningen Online"
    results_message = False

    committee_mail = ""
    committee_message = False

    def __str__(self):
        message = f"{self.intro} {self.contact} {self.end}"
        return message

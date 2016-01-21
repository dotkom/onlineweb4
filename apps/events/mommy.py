# -*- coding: utf-8 -*-
import locale
import logging

from django.utils import timezone
from django.core.mail import EmailMessage

from apps.events.models import AttendanceEvent
from apps.marks.models import Mark, MarkUser
from apps.mommy import schedule
from apps.mommy.registry import Task


class SetEventMarks(Task):

    @staticmethod
    def run():
        logger = logging.getLogger()
        logger.info("Attendance mark setting started")
        locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

        # Gets all active attendance events thats suposed to give automatic marks
        attendance_events = SetEventMarks().active_events()

        for attendance_event in attendance_events:
            SetEventMarks.setMarks(attendance_event, logger)
            message = SetEventMarks.generate_message(attendance_event)

            if message.send:
                EmailMessage(message.subject, unicode(message), message.committee_mail, [],
                             message.not_attended_mails).send()
                logger.info("Emails sent to: " + str(message.not_attended_mails))
            else:
                logger.info("Everyone met. No mails sent to users")

            if message.committee_message:
                EmailMessage(message.subject, message.committee_message, "online@online.ntnu.no",
                             [message.committee_mail]).send()
                logger.info("Email sent to: " + message.committee_mail)

    @staticmethod
    def setMarks(attendance_event, logger=logging.getLogger()):
        event = attendance_event.event
        logger.info('Proccessing "' + event.title + '"')
        mark = Mark()
        mark.title = u"Manglende oppmøte på %s" % event.title
        mark.category = event.event_type
        mark.description = u"Du har fått en prikk på grunn av manglende oppmøte på %s." % event.title
        mark.save()

        for user in attendance_event.not_attended():
            user_entry = MarkUser()
            user_entry.user = user
            user_entry.mark = mark
            user_entry.save()
            logger.info("Mark given to: " + str(user_entry.user))

        attendance_event.marks_has_been_set = True
        attendance_event.save()

    @staticmethod
    def generate_message(attendance_event):
        message = Message()

        not_attended = attendance_event.not_attended()
        event = attendance_event.event
        title = unicode(event.title)

        # return if everyone attended
        if not not_attended:
            return message

        message.not_attended_mails = [user.email for user in not_attended]

        message.committee_mail = event.feedback_mail()
        not_attended_string = u'\n'.join([user.get_full_name() for user in not_attended])

        message.subject = title
        message.intro = u"Hei\n\nPå grunn av manglende oppmøte på \"%s\" har du fått en prikk" % title
        message.contact = u"\n\nEventuelle spørsmål sendes til %s " % message.committee_mail
        message.send = True
        message.committee_message = u"På grunn av manglende oppmøte på \"%s\" har følgende brukere fått en prikk:\n" % \
                                    event.title
        message.committee_message += not_attended_string
        return message

    @staticmethod
    def active_events():
        return AttendanceEvent.objects.filter(automatically_set_marks=True, marks_has_been_set=False,
                                              event__event_end__lt=timezone.now())


class Message():
    subject = ""
    intro = ""
    contact = ""
    not_attended_mails = ""
    send = False
    end = u"\n\nMvh\nLinjeforeningen Online"
    results_message = False

    committee_mail = ""
    committee_message = False

    def __unicode__(self):
        message = "%s %s %s" % (
            self.intro,
            self.contact,
            self.end)
        return message

schedule.register(SetEventMarks, day_of_week='mon-sun', hour=8, minute=05)

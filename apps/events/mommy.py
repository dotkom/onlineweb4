# -*- coding: utf-8 -*-
import locale
import logging

from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from apps.events.models import Event, AttendanceEvent
from apps.marks.models import Mark, MarkUser
from apps.mommy import schedule
from apps.mommy.registry import Task


class SetEventMarks(Task):

    @staticmethod
    def run():
        logger = logging.getLogger(__name__)
        logger.info("Attendance mark setting started")
        locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

        #Gets all active attendance events thats suposed to give automatic marks
        attendance_events = SetEventMarks().active_events()

        for attendance_event in attendance_events:
            SetEventMarks.setMarks(attendance_event, logger)

            not_met = attendance_event.not_attended()

            if len(not_met) > 0:
                SetEventMarks.send_mark_notification(attendance_event)
                SetEventMarks.send_mark_summary(attendance_event)
                logger.info("Marks notifications done")
            else:
                logger.info("Everyone met. No mails sent to users")

    @staticmethod
    def setMarks(attendance_event, logger=logging.getLogger()):
        event = attendance_event.event
        logger.info('Proccessing "' + event.title + '"')
        mark = Mark()
        mark.title = u"Manglende oppmøte på %s" % (event.title)
        mark.category = event.event_type
        mark.description = u"Du har fått en prikk på grunn av manglende oppmøte på %s." % (event.title)
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
    def send_mark_notification(attendance_event):
        logger = logging.getLogger(__name__)

        context = {}
        context['title'] = attendance_event.event.title
        context['contact'] = attendance_event.event.feedback_mail()

        not_met_emails = [user.email for user in attendance_event.not_attended()]

        subject = attendance_event.event.title
        message = render_to_string('events/email/marks_notification.txt', context)

        EmailMessage(subject, unicode(message), context['contact'], [], not_met_emails).send()
        
        logger.info("Mark notification emails sent to: " + str(not_met_emails))

    @staticmethod
    def send_mark_summary(attendance_event):
        context = {}
        context['title'] = attendance_event.event.title
        context['not_met'] = [user for user in attendance_event.not_attended()]

        subject = attendance_event.event.title
        message = render_to_string('events/email/marks_summary_notification.txt', context)

        EmailMessage(subject, unicode(message), "online@online.ntnu.no", [attendance_event.event.feedback_mail()]).send()

    @staticmethod
    def active_events():
        return AttendanceEvent.objects.filter(automatically_set_marks=True, marks_has_been_set=False, event__event_end__lt=timezone.now())


schedule.register(SetEventMarks, day_of_week='mon-sun', hour=8, minute=05)

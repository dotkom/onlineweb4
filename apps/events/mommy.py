# -*- coding: utf-8 -*-
import datetime
import locale

from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage

from apps.events.models import Event, AttendanceEvent, Attendee
from apps.marks.models import Mark, UserEntry
from apps.mommy import Task, schedule

class SetEventMarks(Task):

    @staticmethod
    def run():
        logger = logging.getLogger("feedback")
        logger.info("Attendance mark setting started")
        locale.setlocale(locale.LC_ALL, "nb_NO.UTF-8")

        events = Event.objects.filter(automatic_mark=True, marks_has_belen_set=False)

        for event in events:
            SetEventMarks.setMarks(event)
            message = SetEventMarks.generate_message(event)

            if message.send:
                EmailMessage(message.subject, unicode(message), message.committee_mail, [], message.not_attended_mails).send()

                if message.committee_message:
                    EmailMessage("Event prikker", message.committee_message,"online@online.ntnu.no", [message.committee_mail]).send() 

    @staticmethod
    def setMarks(event, logger):
        logger.info("Proccessing" + event.title)
        mark = Mark()
        mark.title = u"Manglende oppmøte på %s" % (event.title)
        mark.category = event.event_type
        mark.description = u"Du har fått en prikk på grunn av manglende oppmøte på %s." % (event.title)
        mark.save()
        
        for attendee in event.attendance_event.not_attended():
            user_entry = UserEntry()
            user_entry.user = attendee.user
            user_entry.mark = mark
            user_entry.save()
            logger.info("Marks given to: " + user_entry.user)
        
        event.attendanceEvent.marks_has_been_set = True
        event.save()
        

    @staticmethod
    def generate_message(event):
        message = Message()

        not_attended = event.not_attended()

        #return if everyone attended
        if not not_attended:
            return message

        title = event.title    

        
        message.not_attended_mails = [attendee.user.email.encode("utf-8") for attendee in not_attended]

        message.committee_mail = event.feedback_mail()
        not_attended_string = u'\n'.join([attendee.user.get_full_name() for attendee in not_attended])

        message.subject = u"Event: %s" % (title)
        message.intro = u"Hei, på grunn av manglende oppmøte på \"%s\" har du fått en prikk" % (title)
        message.contact = u"\n\nEventuelle spørsmål sendes til %s " % (message.committee_mail)
        message.send = True
        message.committee_message = u"På grunn av manglende oppmøte på \"%s\" har følgende brukere fått en prikk:\n" % (event.title)
        message.committee_message += not_attended_string
        return message


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

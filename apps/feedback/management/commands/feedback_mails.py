# -*- coding: utf-8 -*-

import datetime
import locale

from django.core.management.base import NoArgsCommand
from django.core.mail import EmailMessage
from django.contrib.contenttypes.models import ContentType
from apps.events.models import Event, AttendanceEvent, Attendee
from apps.feedback.models import FeedbackRelation
from apps.marks.models import Mark, UserEntry
import socket

class FeedbackMail():
    today = datetime.date.today()
    yesterday = today + datetime.timedelta(days=-1)
    active_feedbacks = FeedbackRelation.objects.filter(active=True)
   
    for feedback in active_feedbacks:
        not_responded = get_users(feedback)
        #Skip if everyone has answered
        if not not_responded:
            continue
        
        attended_mails = get_user_mails(not_responded)

        locale.setlocale(locale.LC_TIME, 'nb_NO.UTF-8')
        committee_mail = get_committee_email()
        deadline = feedback.deadline.strftime("%d. %B").encode("utf-8")
        title = str(get_title(feedback)).encode("utf-8")
        link = str(u"\n\n" + get_link(feedback)).encode("utf-8")
        results_link = str(get_link(feedback) + "results").encode("utf-8")
        
        deadline_diff = (feedback.deadline - today).days
        day_after_event = start_date + datetime.timedelta(days=1)
        
        message = Message()

        message.subject = u"Feedback: %s" % (title)
        message.intro = u"Hei, vi ønsker tilbakemelding på \"%s\"" % (title)
        message.mark = mark_message(feedback)
        message.contact = u"\n\nEventuelle spørsmål sendes til %s " % (committee_mail)

        if deadline_diff < 0: #Deadline passed
            set_marks(feedback, title, not_responded)
                
            feedback.active = False
            feedback.save()

            message.intro = u"Fristen for å svare på \"%s\" har gått ut og du har fått en prikk." % (title)
            message.mark = ""
            message.start_date = ""
            message.link = ""
            message.send = True
        elif deadline_diff < 1: #Last warning
            message.deadline = u"\n\nI dag innen 23:59 er siste frist til å svare på skjemaet."
            
            results_message = u"Hei, siste purremail på feedback skjema har blitt sendt til alle " \
            u"gjenværende deltagere på \"%s\". Dere kan se feedback-resultatene på\n%s\n" % \
            (title, results_link)
            message.send = True
        elif deadline_diff < 3: # 3 days from the deadline
            message.deadline = u"\n\nFristen for å svare på skjema er %s innen kl 23:59." % (deadline)
            message.send = True
        elif today == day_after_event or send_first_notification: #Day after the event or feedback creation 
            message.deadline = u"\n\nFristen for å svare på skjema er %s innen kl 23:59." % (deadline)
        
            results_message = u"Hei, nå har feedbackmail blitt sendt til alle " \
            u"deltagere på \"%s\". Dere kan se feedback-resultatene på \n%s\n" % \
            (title, results_link)
            message.send = True
       
        if message.send:
            EmailMessage(subject, message, committee_mail, [], attended_mails).send()

        if results_message:
            EmailMessage("Feedback resultat", results_message,"online@online.ntnu.no", [committee_mail]).send()

    def start_date_message(feedback):
        start_date = feedback.get_start_date()

        #If the object(event) doesnt have start date it will send 
        #the first notification the day after the feedbackrelation is made
        if start_date:
            start_date = start_date.date()
            start_date_string = start_date.strftime("%d. %B").encode("utf-8")
            message_start_date = u"som du var med på den %s:" % (start_date_string)
        else:
            message_start_date = ""
        
        return message_start_date   

    def get_users(feedback):
        return feedback.get_slackers()

    def get_user_mails(not_responded):
        return  [user.email for user in not_responded]

    def get_link(feedback):
        hostname = socket.gethostname()
        return str(hostname + feedback.get_absolute_url())

    def get_title(feedback):
        return feedback.get_title()

    def get_committee_email(feedback):
        return feedback.get_mail()

    def mark_message(feedback):
        if feedback.gives_mark:
            return u"\nVær oppmerksom på at du får prikk dersom du ikke svarer " \
            u"på disse spørsmålene innen fristen."
        else:
            return ""

    def set_marks(feedback, title, not_responded):
        mark = Mark()
        mark.title = u"Manglende tilbakemelding på %s" % (title)
        mark.category = 4 #Missed feedback
        mark.description = u"Du har fått en prikk fordi du ikke har levert tilbakemelding."
        mark.save()
        
        for user in not_responded:
            user_entry = UserEntry()
            user_entry.user = user
            user_entry.mark = mark
            user_entry.save()


class Message():
    subject = ""
    intro = ""
    deadline = ""
    mark = ""
    contact = ""
    link = ""
    send = False
    end = u"\n\nMvh\nOnline linjeforening"

    def message():
        message = "%s %s %s %s %s %s %s" % (
            intro, 
            message_start_date, 
            link, 
            deadline, 
            mark, 
            contact, 
            end)


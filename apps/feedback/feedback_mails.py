# -*- coding: utf-8 -*-

import datetime

from django.contrib.contenttypes.models import ContentType

from apps.events.models import Event, AttendanceEvent, Attendee
from apps.feedback.models import FeedbackRelation
from apps.marks.models import Mark, UserEntry

class FeedbackMail():
    @staticmethod
    def generate_message(feedback):
        today = datetime.date.today()
        yesterday = today + datetime.timedelta(days=-1)
        not_responded = FeedbackMail.get_users(feedback)
        #return false if everyone has answered
        if not not_responded:
            return None
        
        message = Message()
        message.attended_mails = FeedbackMail.get_user_mails(not_responded)

        message.committee_mail = FeedbackMail.get_committee_email(feedback)
        deadline = feedback.deadline.strftime("%d. %B").encode("utf-8")
        title = str(FeedbackMail.get_title(feedback)).encode("utf-8")
        message.link = str(u"\n\n" + FeedbackMail.get_link(feedback)).encode("utf-8")
        results_link = str(FeedbackMail.get_link(feedback) + "results").encode("utf-8")
       
        start_date = feedback.get_start_date()
        deadline_diff = (feedback.deadline - today).days

        message.subject = u"Feedback: %s" % (title)
        message.intro = u"Hei, vi ønsker tilbakemelding på \"%s\"" % (title)
        message.mark = FeedbackMail.mark_message(feedback)
        message.contact = u"\n\nEventuelle spørsmål sendes til %s " % (message.committee_mail)
        message.start_date = FeedbackMail.start_date_message(start_date)

        if deadline_diff < 0: #Deadline passed
            FeedbackMail.set_marks(title, not_responded)
                
            feedback.active = False
            feedback.save()

            message.intro = u"Fristen for å svare på \"%s\" har gått ut og du har fått en prikk." % (title)
            message.mark = ""
            message.start_date = ""
            message.link = ""
            message.send = True
        elif deadline_diff < 1: #Last warning
            message.deadline = u"\n\nI dag innen 23:59 er siste frist til å svare på skjemaet."
            
            message.results_message = u"Hei, siste purremail på feedback skjema har blitt sendt til alle " \
            u"gjenværende deltagere på \"%s\".\nDere kan se feedback-resultatene på:\n%s\n" % \
            (title, results_link)
            message.send = True
        elif deadline_diff < 3: # 3 days from the deadline
            message.deadline = u"\n\nFristen for å svare på skjema er %s innen kl 23:59." % (deadline)
            message.send = True
        elif FeedbackMail.send_first_notification(feedback): #Day after the event or feedback creation 
            message.deadline = u"\n\nFristen for å svare på skjema er %s innen kl 23:59." % (deadline)
        
            message.results_message = u"Hei, nå har feedbackmail blitt sendt til alle " \
            u"deltagere på \"%s\".\nDere kan se feedback-resultatene på:\n%s\n" % \
            (title, results_link)
            message.send = True

        return message
        
    @staticmethod
    def send_first_notification(feedback):
        start_date = FeedbackMail.start_date(feedback)

        if not start_date:
            yesterday = datetime.date() - datetime.timedelta(days=1)
            #The object that requires feedback doesnt have a start date
            if feedback.created_date == yesterday.date():
                #Send the first notification the day after the feedback relation was created
                return True
        else:
            day_after_event = start_date + datetime.timedelta(1)
            if day_after_event == datetime.date.today():
                #Send the first notification the day after the event
                return True
        return False

    @staticmethod
    def start_date(feedback):
        start_date = feedback.get_start_date()
        
        if start_date:
            return start_date.date()
        else:
            return False

    @staticmethod
    def start_date_message(start_date):
        #If the object(event) doesnt have start date it will send 
        #the first notification the day after the feedbackrelation is made
        if start_date:
            start_date_string = start_date.strftime("%d. %B").encode("utf-8")
            message_start_date = u"som du var med på den %s:" % (start_date_string)
        else:
            message_start_date = ""
        
        return message_start_date   

    @staticmethod
    def get_users(feedback):
        return feedback.get_slackers()

    @staticmethod
    def get_user_mails(not_responded):
        return  [user.email for user in not_responded]

    @staticmethod
    def get_link(feedback):
        #hostname = socket.gethostname()
        #TODO Hostname returns name of the server, not the url of the running django application, look into alternative solution
        return str("www.online.ntnu.no" + feedback.get_absolute_url())

    @staticmethod
    def get_title(feedback):
        return feedback.get_title()

    @staticmethod
    def get_committee_email(feedback):
        return feedback.get_email()

    @staticmethod
    def mark_message(feedback):
        if feedback.gives_mark:
            return u"\nVær oppmerksom på at du får prikk dersom du ikke svarer " \
            u"på disse spørsmålene innen fristen."
        else:
            return ""

    @staticmethod
    def set_marks(title, not_responded):
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
    start_date = ""
    deadline = ""
    mark = ""
    contact = ""
    link = ""
    send = False
    end = u"\n\nMvh\nOnline linjeforening"
    results_message = False

    committee_mail = ""
    attended_mails = False


    def __unicode__(self):
        message = "%s %s %s %s %s %s %s" % (
            self.intro, 
            self.start_date, 
            self.link, 
            self.deadline, 
            self.mark, 
            self.contact, 
            self.end)
        return message


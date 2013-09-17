# -*- coding: utf-8 -*-

import datetime
import locale

from django.core.management.base import NoArgsCommand
from django.core.mail import EmailMessage

class Command(NoArgsCommand):
    help = "Loops trough active feedbacks and sends mails to attendees. Run it once a day"

    def handle_noargs(self, **options):
        from django.contrib.contenttypes.models import ContentType
        from apps.events.models import Event, AttendanceEvent, Attendee
        from apps.feedback.models import FeedbackRelation
        from apps.marks.models import Mark, UserEntry
        
        today = datetime.date.today()
        yesterday = today + datetime.timedelta(days=-1)

        active_feedbacks = FeedbackRelation.objects.filter(active=True)

       
        for feedback in active_feedbacks:
            not_responded = feedback.get_slackers()
            #Skip if everyone has answered
            if not not_responded:
                continue
            

            locale.setlocale(locale.LC_TIME, 'nb_NO.UTF-8')
            committee_mail = feedback.get_email()
            deadline = feedback.deadline.strftime("%d. %B").encode("utf-8")
            title = str(feedback.get_title()).encode("utf-8")
            link = str(u"\n\nwww.online.ntnu.no" + feedback.get_absolute_url()).encode("utf-8")
            results_link = str(u"www.online.ntnu.no" + feedback.get_absolute_url() + "results").encode("utf-8")
            
            send_first_notification = False
            start_date = feedback.get_start_date()
            if start_date:
                start_date = start_date.date()
                day_after_event = start_date + datetime.timedelta(days=1)
                start_date_string = start_date.strftime("%d. %B").encode("utf-8")
            else:
                if feedback.created_date == yesterday:
                    send_first_notification = True
            
            attended_mails = [user.email for user in not_responded]
            
            deadline_diff = (feedback.deadline - today).days

            results_message = False
            send_message = False

            subject = u"Feedback: %s" % (title)
            message_intro = u"Hei, vi ønsker tilbakemelding på \"%s\"" % (title)
            message_start_date = ""
            if start_date:
                message_start_date = u"som du var med på den %s:" % (start_date_string)
           
            message_deadline = ""
            
            message_mark = ""
            if feedback.gives_mark:
                message_mark = u"\nVær oppmerksom på at du får prikk dersom du ikke svarer " \
                u"på disse spørsmålene innen fristen."

            message_contact = u"\n\nEventuelle spørsmål sendes til %s " % (committee_mail)
            message_end = u"\n\nMvh\nOnline linjeforening"

            if deadline_diff < 0: #Deadline passed
                if feedback.gives_mark:
                    user_entry = UserEntry()
                    for user in not_responded:
                        #TODO test med flere brukere
                        mark = Mark()
                        mark.title = u"manglende tilbakemelding på %s" % (title)
                        mark.category = 4 #Missed feedback
                        mark.description = u"Du har fått en prikk fordi du ikke har levert tilbakemelding."
                        mark.save()
                        user_entry.user = user
                        user_entry.mark = mark
                    user_entry.save()
                    
                    #feedback.active = False
                    #feedback.save()
                    message_intro = u"Fristen for å svare på \"%s\" har gått ut og du har fått en prikk." % (title)
                    message_mark = ""
                    message_start_date = ""
                    link = ""
                    send_message = True
            elif deadline_diff < 1: #Last warning
                message_deadline = u"\n\nI dag innen 23:59 er siste frist til å svare på skjemaet."
                
                results_message = u"Hei, siste purre-mail på feedback skjema har blitt sendt til alle " \
                u"gjenværende deltagere på \"%s\". Dere kan se feedback-resultatene på\n%s\n" % \
                (title, results_link)
                send_message = True
            elif deadline_diff < 3: # 3 days from the deadline
                message_deadline = u"\n\nFristen for å svare på skjema er %s innen kl 23:59." % (deadline)
                send_message = True
            elif today == day_after_event or send_first_notification: #Day after the event or feedback creation 
                message_deadline = u"\n\nFristen for å svare på skjema er %s innen kl 23:59." % (deadline)
            
                results_message = u"Hei, nå har feedbackmail blitt sendt til alle " \
                u"deltagere på \"%s\". Dere kan se feedback-resultatene på \n%s\n" % \
                (title, results_link)
                send_message = True
           
            if send_message:
                message = "%s %s %s %s %s %s %s" % (
                    message_intro, 
                    message_start_date, 
                    link, 
                    message_deadline, 
                    message_mark, 
                    message_contact, 
                    message_end)
                EmailMessage(subject, message, committee_mail, [], attended_mails).send()

            if results_message:
                EmailMessage("Feedback resultat", results_message,"online@online.ntnu.no", [committee_mail]).send()

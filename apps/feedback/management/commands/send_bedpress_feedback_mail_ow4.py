# -*- coding: utf-8 -*-

import datetime
import locale

from django.core.management.base import NoArgsCommand
from django.core.mail import EmailMessage

class Command(NoArgsCommand):
    help = "Sender mail til alle deltagere på bedriftpresentasjon i dag om feedback. Kjøres maks en gang om dagen"

    def handle_noargs(self, **options):
        from django.contrib.contenttypes.models import ContentType
        from apps.events.models import Event, AttendanceEvent, Attendee
        from apps.feedback.models import FeedbackRelation
        
        today = datetime.date.today()
        yesterday = today + datetime.timedelta(days=-1)

        activeFeedbacks = FeedbackRelation.objects.filter(active=True)
       
        for feedback in activeFeedbacks:
            not_responded = feedback.get_slackers()
            #Skip if everyone has answered
            if not not_responded:
                continue
            
            start_date = feedback.get_start_date().date()
            if not start_date:
                #TODO fix hvis det ikke er noe start dato
                continue
            day_after_event = start_date + datetime.timedelta(days=1)
            locale.setlocale(locale.LC_TIME, 'nb_NO.UTF-8')
            committee_mail = feedback.get_email()
            deadline = feedback.deadline.strftime("%d. %B").encode("utf-8")
            title = str(feedback.get_title()).encode("utf-8")
            link = str("www.online.ntnu.no" + feedback.get_absolute_url()).encode("utf-8")
            results_link = str("www.online.ntnu.no" + feedback.get_absolute_url() + "results").encode("utf-8")
            start_date_string = start_date.strftime("%d. %B").encode("utf-8")
            
            attended_mails = [user.email for user in not_responded]

            deadline_diff = (feedback.deadline - today).days

            results_message = False
            message = False


            if deadline_diff < 0: #Deadline passed
                #Gi prikker
                #Fix Message
                feedback.active = False
                feedback.save()
            elif deadline_diff < 1: #Last warning
                message = "Hei, du var med på \"%s\" den %s. Dette er siste " \
                "mulighet til å gi tilbakemelding ved å svare på noen" \
                "spørsmål: \n\n%s\n\nVær oppmerksom på at du får prikk dersom du ikke svarer " \
                "på disse spørsmålene innen klokka 23:59.\nTakk for hjelpen\n\n"\
                "\nEventuelle spørsmål sendes til %s\n" \
                "\nMvh\nOnline linjeforening" % (title,
                    start_date_string, link, committee_mail)
                
                results_message = "Hei, siste purre-mail på feedback skjema har blitt sendt til alle " \
                "deltagere på \"%s\". Dere kan nå feedback-resultatene på %s\n" % \
                (title, results_link)
            elif deadline_diff < 3: # 3 days from the deadline
                message = "Du har enda ikke svart på tilbakemeldingen etter"\
                " %s. Du har frist innen %s klokka 23:59. Dersom du ikke har svart"\
                " på tilbakemeldingen innen denne tid vil du få en prikk.\n\n"\
                "lenke:\n\n%s\n"\
                "\nEventuelle spørsmål sendes til %s\n" \
                "\nMvh\nOnline linjeforening" % (title, deadline, link, committee_mail)
            elif today == day_after_event: #Day after the event 
                message = "Hei, du var med på \"%s\" den %s. For å gi " \
                "tilbakemelding til bedriften ønsker vi at du svarer på noen " \
                "spørsmål: \n\n%s\n\nVær oppmerksom på at du får prikk dersom du ikke svarer " \
                "på disse spørsmålene innen %s klokka 23:59.\nTakk for hjelpen\n\n"\
                "\nEventuelle spørsmål sendes til %s\n" \
                "\nMvh\nOnline linjeforening" % (title,
                    start_date_string, link, deadline, committee_mail)
            
                results_message = "Hei, nå har feedbackmail blitt sendt til alle " \
                "deltagere på \"%s\". Dere kan se feedback-resultatene på \n%s\n" % \
                (title, results_link)

            if message:
                EmailMessage("Feedback", message, committee_mail, [], attended_mails).send()
            if results_message:
                EmailMessage("Feedback resultat", results_message,"online@online.ntnu.no", [committee_mail]).send()

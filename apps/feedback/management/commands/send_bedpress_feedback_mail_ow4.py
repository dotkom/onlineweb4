# -*- coding: utf-8 -*-

import datetime
import locale

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.core.mail import EmailMessage

class Command(NoArgsCommand):
    help = "Sender mail til alle deltagere på bedriftpresentasjon i dag om feedback. Kjøres maks en gang om dagen"

    def handle_noargs(self, **options):
        from django.contrib.contenttypes.models import ContentType
        from apps.events.models import Event, AttendanceEvent, Attendee
        from apps.feedback.models import FeedbackRelation
        yesterday = datetime.date.today() + datetime.timedelta(days= -1)
        notice_date = datetime.date.today() + datetime.timedelta(days= -4)
       
        events = Event.objects.filter(event_start__year=
                yesterday.year, event_start__month=yesterday.month,
                event_start__day=yesterday.day, event_type=2)  # 2 = bedpress
        notices = Event.objects.filter(event_start__year=
                notice_date.year, event_start__month=notice_date.month,
                event_start__day=notice_date.day, event_type=2)  # 2 = bedpress

        # Cant make methods so the lists are joined and looped to avoid duplicated code
        events_count = len(events)
        events = events | notices

        for (counter, event) in enumerate(events):
            #Generic magic to get the feedback relations connected to the event
            feedback_type = ContentType.objects.get(model="feedbackrelation")
            feedbacks = feedback_type.get_all_objects_for_this_type(object_id=event.id)
            
            # skip if the event has no feedback relation
            if not feedbacks:
                continue
            
            attended = map(lambda x: getattr(x, 'user'),
                Attendee.objects.filter(event=event, attended=True))
           
            link = ""
            bedkom_link = ""
            for  feedback in feedbacks:
                link += "https://online.ntnu.no/feedback/events/event/%d/%d\n" % (event.id, feedback.id)
                bedkom_link += "https://online.ntnu.no/feedback/events/event/%d/%d/results\n" % (event.id, feedback.id)
    
            link.encode("utf-8")
            bedkom_link.encode("utf-8")
            

            timedelta = datetime.timedelta(days=4)
            deadline = timedelta + event.event_start

            #strings must be utf-8
            locale.setlocale(locale.LC_TIME, 'nb_NO.UTF-8')
            deadline = deadline.strftime("%d. %B").encode("utf-8")
            start_date = event.event_start.strftime("%d. %B").encode("utf-8")
            title = event.title.encode("utf-8")
            
            # Checks if the events list is over on the deadline notices
            if counter < events_count:
                mails = [user.email for user in attended]
                # mail to attendees
                message = "Hei, du var med på \"%s\" den %s. For å gi " \
                "tilbakemelding til bedriften ønsker vi at du svarer på noen " \
                "spørsmål: \n%s\n\nVær oppmerksom på at du får prikk dersom du ikke svarer " \
                "på disse spørsmålene innen %s klokka 23:59.\nTakk for hjelpen\n\n"\
                "\nEventuelle spørsmål sendes til bedkom@online.ntnu.no\n" \
                "\nMvh\nOnline linjeforening" % (title,
                        start_date, link, deadline)
            
                # mail til bedkom
                bedkom_message = "Hei, nå har feedbackmail blitt sendt til alle " \
                "deltagere på \"%s\". Dere kan nå feedback-resultatene på %s\n" % \
                (title, bedkom_link)
                
                EmailMessage("Bedpres feedback", message, "bedkom@online.ntnu.no", [], mails).send()
                EmailMessage("Bedpres feedback view", bedkom_message,"online@online.ntnu.no", [settings.EMAIL_BEDKOM]).send()
            else: #Event is a notice
                not_responded = {}
                for feedback in feedbacks:
                    not_responded_temp = set(attended).difference(set(feedback.answered.all()))
                    
                    not_responded = set(list(not_responded) + list(not_responded_temp))

                if not not_responded:
                    continue

                mails = [user.email for user in not_responded]
               # mail to attendees
                message = "Du har enda ikke svart på tilbakemeldingen etter"\
                " %s. Du har frist innen %s klokka 23:59. Dersom du ikke har svart"\
                " på tilbakemeldingen innen denne tid vil du få en prikk.\n\n"\
                "lenke:\n%s\n"\
                "\nEventuelle spørsmål sendes til bedkom@online.ntnu.no\n" \
                "\nMvh\nOnline linjeforening" % (title, deadline, link)

                EmailMessage("Purring: Bedpres tilbakemelding", message,
                    "bedkom@online.ntnu.no", [], mails).send()

                # mail to bedkom
                bedkom_link = "https://online.ntnu.no/feedback/events/event/%d/%d/results" % (event.id, feedback.id)
                bedkom_message = "Hei, nå har feedbackmail blitt sendt til alle " \
                "deltagere på \"%s\". Dere kan nå feedback-resultatene på %s\n" % \
                (event.title.encode("utf-8"), bedkom_link.encode("utf-8"))
                
                EmailMessage("purring sendt til deltagere", bedkom_message,
                    "online@online.ntnu.no", [settings.EMAIL_BEDKOM]).send()
            

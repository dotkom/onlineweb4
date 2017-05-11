import logging

from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from apps.contact.forms import ContactForm


# Index page
def index(request):
    context = {'form': ContactForm}
    return render_to_response('contact/index.html', context, context_instance=RequestContext(request))


def contact_submit(request):

    log = logging.getLogger(__name__)

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():

            name = form.cleaned_data['contact_name']
            content = form.cleaned_data['content']
            from_email = form.cleaned_data['contact_email']
            to_email = [form.cleaned_data['contact_receiver']]

            if not name:
                name = 'Noen'

            if request.user.is_authenticated:
                username = request.user.username
                log.info('{username} has tried to contact {to_email}'.format(username=username, to_email=to_email))
            else:
                # add logging of IP if not logged in



            subject = '[Kontakt] {name} har kontaktet dere gjennom online.ntnu.no'.format(
                name=name)

            EmailMessage(subject, content, from_email, to_email).send()
            messages.success(request, 'Mailen ble sendt')
        else:
            messages.error(request, 'Mail ble ikke sendt, prøv igjen eller send mail direkte til dotkom ')
    return redirect('contact_index')

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
                # messages.error(request, client_ip)
                print('Her skal jeg logge IP')

            subject = '[Kontakt] {name} har kontaktet dere gjennom online.ntnu.no'.format(
                name=name)

            EmailMessage(subject, content, from_email, to_email).send()
            messages.success(request, 'Meldingen ble sendt')
        else:
            client_ip = get_client_ip(request)
            messages.error(request, 'Meldingen ble ikke sendt. Prøv igjen eller send mail direkte til dotkom' + client_ip)
    return redirect('contact_index')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

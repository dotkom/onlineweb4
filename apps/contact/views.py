import logging

from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from apps.contact.forms import ContactForm


# Index page
def index(request):
    context = {'form': ContactForm}
    return render(request, 'contact/index.html', context)


def contact_submit(request):

    log = logging.getLogger(__name__)

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():

            name = form.cleaned_data['contact_name']
            content = form.cleaned_data['content']
            from_email = form.cleaned_data['contact_email']
            to_email = [form.cleaned_data['contact_receiver']]
            client_ip = get_client_ip(request)

            if not name:
                name = 'Noen'

            if request.user.is_authenticated:
                username = request.user.username
                log.info('{username} has tried to contact {to_email}'.format(username=username, to_email=to_email))
            else:
                log.info('A user at {client_ip} has tried to contact {to_email}'.format(
                    client_ip=client_ip, to_email=to_email))

            subject = '[Kontakt] {name} har kontaktet dere gjennom online.ntnu.no'.format(
                name=name)

            EmailMessage(subject, content, from_email, to_email).send()
            messages.success(request, 'Meldingen ble sendt')
        else:
            messages.error(request, 'Meldingen ble ikke sendt. Prøv igjen eller send mail direkte til dotkom')
    return redirect('contact_index')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

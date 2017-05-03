from django.core.mail import EmailMessage
from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from apps.contact.forms import ContactForm


# Index page
def index(request):
    context = {'form': ContactForm}
    return render_to_response('contact/index.html', context, context_instance=RequestContext(request))


def contact_submit(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['contact_receiver'] == '1':
                choice = ['hovedstyret@online.ntnu.no']
            else:
                choice = ['dotkom@online.ntnu.no']

            subject = '[Kontakt]' + form.cleaned_data['contact_name'] + 'har kontaktet dere gjennom ow4'
            content = form.cleaned_data['content']
            from_email = form.cleaned_data['contact_email']
            to_email = choice

            EmailMessage(subject, content, from_email, to_email).send()
            messages.success(request, 'Mailen ble sendt')
        else:
            messages.error(request, 'Mail ble ikke sendt')
    return redirect('contact_index')

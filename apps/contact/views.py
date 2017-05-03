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
            EmailMessage('subject', form.cleaned_data['content'], form.cleaned_data['contact_email'],
            ['dotkom@online.ntnu.no']).send()
            messages.success(request, 'Mailen ble sendte')
        else:
            messages.error(request, 'Mail ble ikke sendt')
    return redirect('contact_index')

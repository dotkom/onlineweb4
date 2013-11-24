#-*- coding: utf-8 -*-
import json
import os
import uuid

from PIL import Image

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext as _

from apps.authentication.forms import NewEmailForm
from apps.authentication.models import Email, RegisterToken
from apps.marks.models import Mark
from apps.profiles.forms import ImageForm, MailSettingsForm, PrivacyForm, ProfileForm, MembershipSettingsForm

"""
Index for the entire user profile view
Methods redirect to this view on save
"""
@login_required
def index(request):

    """
    This view is rendered for ever request made to the userprofile pages,
    due to the fact that it is a one-page view.
    """

    dictionary = _create_request_dictionary(request)

    # When a user clicks on one of the navigation tabs, a session key will be set.
    # This enables us to return the user to the correct tab when returning the view.
    # If no session key is set, return the user to the default first tab

    return render(request, 'profiles/index.html', dictionary)


def _create_request_dictionary(request):

    dictionary = {
        'privacy_form' : PrivacyForm(instance=request.user.privacy),
        'user_profile_form' : ProfileForm(instance=request.user),
        'image_form' : ImageForm(instance=request.user),
        'password_change_form' : PasswordChangeForm(request.user),
        'marks' : [
            # Tuple syntax ('title', list_of_marks, is_collapsed)
            (_(u'aktive prikker'), Mark.active.all().filter(given_to=request.user), False),
            (_(u'inaktive prikker'), Mark.inactive.all().filter(given_to=request.user), True),
        ],
        'mail_settings' : MailSettingsForm(instance=request.user),
        'new_email' : NewEmailForm(),
        'membership_settings' : MembershipSettingsForm(instance=request.user),
    }

    if request.session.has_key('userprofile_active_tab'):
        dictionary['active_tab'] = request.session['userprofile_active_tab']
    else:
        dictionary['active_tab'] = 'myprofile'

    return dictionary


@login_required
def update_active_tab(request):

    if request.is_ajax():
        if request.method == 'POST':
            value = json.loads(request.body)
            request.session['userprofile_active_tab'] = value['active_tab']

            return HttpResponse(status=200)
    return HttpResponse(status=405)


@login_required
def save_user_profile(request):

    if request.method == 'POST':

        user = request.user
        dictionary = _create_request_dictionary(request)
        user_profile_form = ProfileForm(request.POST)
        dictionary['user_profile_form'] = user_profile_form

        if not user_profile_form.is_valid():
            messages.error(request, _(u"Noen av de påkrevde feltene mangler"))
            return render(request, 'profiles/index.html', dictionary)

        cleaned = user_profile_form.cleaned_data

        user.address = cleaned['address']
        user.allergies = cleaned['allergies']
        user.mark_rules = cleaned['mark_rules']
        user.nickname = cleaned['nickname']
        user.phone_number = cleaned['phone_number']
        user.website = cleaned['website']
        user.zip_code = cleaned['zip_code']
        user.gender = cleaned['gender']

        user.save()
        messages.success(request, _(u"Brukerprofilen din ble endret"))

    return redirect("profiles")


@login_required
def upload_image(request):

    if request.method != "POST":
        return redirect("profiles")

    uploaded_file = None

    if request.FILES['image']:
        uploaded_file = request.FILES['image']

    # How to verify that it IS an image? Possible object injection hack
    # Please check
    if uploaded_file is None and uploaded_file.content_type:
        messages.error(request, _(u"Ingen bildefil ble valgt"))
        return redirect("profiles")

    return _handle_image_upload(request, uploaded_file)


def _handle_image_upload(request, image):

    try:
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, "images", "profiles")):
            os.makedirs(os.path.join(settings.MEDIA_ROOT, "images", "profiles"))

        extension_index = image.name.rfind('.')

        #Make sure the image contains a file extension
        if extension_index == -1:
            messages.error(request, _(u"Filnavnet inneholder ikke filtypen"))
            return redirect("profiles")

        #remove already existing profile image, in case new extension is different from already existing
        remove_file(request)

        #Prepare filename and open-create a new file if it does not exist
        extension = image.name[extension_index:]
        filename = os.path.join(settings.MEDIA_ROOT, "images", "profiles", request.user.username + extension)
        destination = open(filename, 'wb+')

        #Write the image uncropped
        for chunk in image.chunks():
            destination.write(chunk)
        destination.close()

        #Create cropping bounding box
        box = (int(float(request.POST['x'])), int(float(request.POST['y'])), int(float(request.POST['x2'])), int(float(request.POST['y2'])))
        img = Image.open(filename)
        crop_img = img.crop(box)
        #Saving the image here so we release the lock on the file
        img.save(filename)
        #Actual cropping save
        crop_img.save(filename)
        #Set media url for user image
        request.user.image = os.path.join(settings.MEDIA_URL, "images", "profiles", request.user.username + extension)
        request.user.save()

    except Exception:
        if request.is_ajax():
            return HttpResponse(status=500, content=json.dumps({ 'message': _(u"Bildet kunne ikke lagres.") }))
        else:
            messages.error(request, _(u"Bildet kunne ikke lagres."))
            return redirect("profiles")

    if request.is_ajax():
        return HttpResponse(status=200, content=json.dumps({'message' : _(u"Bildet ble lagret."), 'image-url' : request.user.get_image_url() }))
    else:
        messages.success(request, _(u"Bildet ble lagret."))
        return redirect("profiles")


@login_required
def confirm_delete_image(request):

    if request.is_ajax():
        if request.method == 'DELETE':
            if "/profiles/" in request.user.get_image_url():
                remove_file(request)
                return HttpResponse(status=200, content=json.dumps({'message': _(u"Ditt bilde har blitt fjernet."), 'url' : request.user.get_image_url() }))
        return HttpResponse(status=412, content=json.dumps({'message': _(u"Du har ikke lastet opp noe bilde å fjerne.") }))
    else:
        return redirect("profiles")


@login_required
def remove_file(request):

    if "/profiles/" in request.user.get_image_url():
        extension_index = request.user.image.name.rfind('.')
        extension = request.user.image.name[extension_index:]
        filename = os.path.join(settings.MEDIA_ROOT, "images", "profiles", request.user.username + extension)
        request.user.image = None
        request.user.save()
        os.remove(filename)


@login_required
def save_privacy(request):

    if request.method == 'POST':
        dictionary = _create_request_dictionary(request)
        privacy_form = PrivacyForm(request.POST, instance=request.user.privacy)
        dictionary['privacy_form'] = privacy_form

        if not privacy_form.is_valid():
            messages.error(request, _(u"Noen av de påkrevde feltene mangler"))
            return render(request, 'profiles/index.html', dictionary)

        privacy_form.save()
        messages.success(request, _(u"Personvern ble endret"))

    return redirect("profiles")


@login_required
def save_password(request):

    if request.method == 'POST':
        dictionary = _create_request_dictionary(request)
        password_change_form = PasswordChangeForm(user=request.user, data=request.POST)
        dictionary['password_change_form'] = password_change_form

        if not password_change_form.is_valid():
            messages.error(request, _(u"Passordet ditt ble ikke endret"))
            return render(request, 'profiles/index.html', dictionary)

        password_change_form.save()
        messages.success(request, _(u"Passordet ditt ble endret"))

    return redirect("profiles")


@login_required
def add_email(request):

    if request.method == 'POST':
        form = NewEmailForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            email_string = cleaned['new_email']

            # Check if the email already exists
            if Email.objects.filter(email=cleaned['new_email']).count() > 0:
                messages.error(request, _(u"Eposten %s er allerede registrert.") % email_string)
                return redirect('profiles')

            # Create the email
            email = Email(email=email_string, user=request.user)
            email.save()

            # Send the verification mail
            _send_verification_mail(request, email.email)

            messages.success(request, _(u"Eposten ble lagret. Du må sjekke din innboks for å verifisere den."))
        
    return redirect('profiles')
    

@login_required
def delete_email(request):

    if request.is_ajax():
        if request.method == 'POST':
            email_string = request.POST.get('email')
            email = get_object_or_404(Email, email=email_string)
            
            # Check if the email belongs to the registered user
            if email.user != request.user:
                return HttpResponse(status=412, content=json.dumps(
                                                    {'message': _(u"%s er ikke en eksisterende epostaddresse på din profil.") % email.email}
                                                ))

            # Users cannot delete their primary email, to avoid them deleting all their emails
            if email.primary:
                return HttpResponse(status=412, content=json.dumps({'message': _(u"Kan ikke slette primær-epostadresse.")}))
            
            email.delete()
            return HttpResponse(status=200)
    return HttpResponse(status=404)


@login_required
def set_primary(request):

    if request.is_ajax():
        if request.method == 'POST':
            email_string = request.POST.get('email')
            email = get_object_or_404(Email, email=email_string)

            # Check if the email belongs to the registered user
            if email.user != request.user:
                return HttpResponse(status=412, content=json.dumps(
                                                    {'message': _(u"%s er ikke en eksisterende epostaddresse på din profil.") % email.email}
                                                ))

            # Check if it was already primary
            if email.primary:
                return HttpResponse(status=412, content=json.dumps(
                                                    {'message': _(u"%s er allerede satt som primær-epostaddresse.") % email.email}
                                                ))

            # Deactivate the old primary, if there was one
            primary_email = request.user.get_email()
            if primary_email:
                primary_email.primary = False
                primary_email.save()
            # Activate new primary
            email.primary = True
            email.save()

            return HttpResponse(status=200)
    return HttpResponse(status=404)


@login_required
def verify_email(request):

    if request.is_ajax():
        if request.method == 'POST':
            email_string = request.POST.get('email')
            email = get_object_or_404(Email, email=email_string)

            # Check if the email belongs to the registered user
            if email.user != request.user:
                return HttpResponse(status=412, content=json.dumps(
                                                    {'message': _(u"%s er ikke en eksisterende epostaddresse på din profil.") % email.email}
                                                ))

            # Check if it was already verified
            if email.verified:
                return HttpResponse(status=412, content=json.dumps(
                                                    {'message': _(u"%s er allerede verifisert.") % email.email}
                                                ))

            # Send the verification mail
            _send_verification_mail(request, email.email)

            return HttpResponse(status=200)
    return HttpResponse(status=404)


def _send_verification_mail(request, email):

    # Create the registration token
    token = uuid.uuid4().hex
    rt = RegisterToken(user=request.user, email=email, token=token)
    rt.save()

    email_message = _(u"""
En ny epost har blitt registrert på din profil på online.ntnu.no.

For å kunne ta eposten i bruk kreves det at du verifiserer den. Du kan gjore dette
ved å besøke lenken under.

http://%s/auth/verify/%s/

Denne lenken vil være gyldig i 24 timer. Dersom du behøver å få tilsendt en ny lenke
kan dette gjøres ved å klikke på knappen for verifisering på din profil.
""") % (request.META['HTTP_HOST'], token)

    send_mail(_(u'Verifiser din epost %s') % email, email_message, settings.DEFAULT_FROM_EMAIL, [email,])


@login_required
def save_membership_details(request):

    if request.is_ajax():
        if request.method == 'POST':
            form = MembershipSettingsForm(request.POST)
            if form.is_valid():
                cleaned = form.cleaned_data
                request.user.field_of_study = cleaned['field_of_study']
                request.user.started_date = cleaned['started_date']
                
                request.user.save()

                return HttpResponse(status=200)
            else:
                field_errors = []
                form_errors = form.errors.items()
                for form_error in form_errors:
                    for field_error in form_error[1]:
                        field_errors.append(field_error)

                return HttpResponse(status=412, content=json.dumps({'message': ", ".join(field_errors)}))

    return HttpResponse(status=404) 

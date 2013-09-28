#-*- coding: utf-8 -*-
import json
import os

from PIL import Image

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import ugettext as _

from apps.marks.models import Mark
from apps.profiles.forms import PrivacyForm, ProfileForm


"""
    Index for the entire user profile view
    Methods redirect to this view on save
"""
def index(request):

    """
    This view is rendered for ever request made to the userprofile pages,
    due to the fact that it is a one-page view.
    """

    if not request.user.is_authenticated():
        return render_home(request)

    dict = create_request_dictionary(request)

    # If a user has made a post, a session value will be set for which tab the user posted from.
    # This enables us to return the user to the correct tab when returning the view.
    # If no session key is set, return the user to the default first tab

    return render(request, 'profiles/index.html', dict)


def render_home(request):
    messages.error(request, _(u"Du er ikke logget inn, og kan ikke se din profil."))
    return redirect('home')


def create_request_dictionary(request):

    dict = {
        'privacy_form' : PrivacyForm(instance=request.user.privacy),
        'user_profile_form' : ProfileForm(instance=request.user),
        'password_change_form' : PasswordChangeForm(request.user),
        'marks' : [
            # Tuple syntax ('title', list_of_marks, is_collapsed)
            (_(u'aktive prikker'), Mark.active.all().filter(given_to=request.user), False),
            (_(u'inaktive prikker'), Mark.inactive.all().filter(given_to=request.user), True),
        ]
    }

    if request.session.has_key('userprofile_active_tab'):
         dict['active_tab'] = request.session['userprofile_active_tab']
    else:
        dict['active_tab'] = 'myprofile'

    return dict


def updateActiveTab(request):

    if request.is_ajax():
        if request.method == 'POST':
            value = json.loads(request.body)
            request.session['userprofile_active_tab'] = value['active_tab']

            return HttpResponse(status=200)
    return HttpResponse(status=405)

def saveUserProfile(request):

    if not request.user.is_authenticated():
        return render_home(request)

    if request.method == 'POST':

        user = request.user
        dict = create_request_dictionary(request)
        user_profile_form = ProfileForm(request.POST, request.FILES)
        dict['user_profile_form'] = user_profile_form

        if not user_profile_form.is_valid():
            messages.error(request, _(u"Noen av de påkrevde feltene mangler"))
            return render(request, 'profiles/index.html', dict)

        user.address = user_profile_form.cleaned_data['address']
        user.allergies = user_profile_form.cleaned_data['allergies']
        user.area_code = user_profile_form.cleaned_data['address']
        user.infomail = user_profile_form.cleaned_data['infomail']
        user.mark_rules = user_profile_form.cleaned_data['mark_rules']
        user.nickname = user_profile_form.cleaned_data['nickname']
        user.phone_number = user_profile_form.cleaned_data['phone_number']
        user.website = user_profile_form.cleaned_data['website']
        user.email = user_profile_form.cleaned_data['email']

        user.save()
        messages.success(request, _(u"Brukerprofilen din ble endret"))

    return redirect("profiles")


def uploadImage(request):

    if request.method != "POST":
        return redirect("profiles")

    file = None

    if request.FILES['image']:
        file = request.FILES['image']

    # How to verify that it IS an image? Possible object injection hack
    # Please check
    if file is None and file.content_type:
        messages.error(request, _(u"Ingen bildefil ble valgt"))
        return redirect("profiles")

    return handleImageUpload(request, file)


def handleImageUpload(request, image):

    try:
        extension_index = image.name.rfind('.')

        #Make sure the image contains a file extension
        if extension_index == -1:
            messages.error(request, _(u"Filnavnet inneholder ikke filtypen"))
            return redirect("profiles")

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
            return HttpResponse(status=500, content=_(u"Bildet kunne ikke lagres"))
        else:
            messages.error(request, _(u"Bildet kunne ikke lagres"))
            return redirect("profiles")

    if request.is_ajax():
        #Dumping object as json does not work with ugettext_lazy
        return HttpResponse(status=200, content=json.dumps(
            {'message' : _(u"Bildet ble lagret"), 'image-url' : request.user.image.name }
        ))
    else:
        messages.success(request, _(u"Bildet ble lagret"))
        return redirect("profiles")



def confirmDeleteImage(request):

    if request.is_ajax():
        if request.method == 'DELETE':
            request.user.image = None
            request.user.save()

            return HttpResponse(status=204)
    return HttpResponse(status=405)


def savePrivacy(request):

    if not request.user.is_authenticated():
        return render_home(request)

    if request.method == 'POST':
        dict = create_request_dictionary(request)
        privacy_form = PrivacyForm(request.POST, instance=request.user.privacy)
        dict['privacy_form'] = privacy_form

        if not privacy_form.is_valid():
            messages.error(request, _(u"Noen av de påkrevde feltene mangler"))
            return render(request, 'profiles/index.html', dict)

        privacy_form.save()
        messages.success(request, _(u"Personvern ble endret"))

    return redirect("profiles")


def savePassword(request):

    if not request.user.is_authenticated():
        return render_home(request)

    if request.method == 'POST':
        dict = create_request_dictionary(request)
        password_change_form = PasswordChangeForm(user=request.user, data=request.POST)
        dict['password_change_form'] = password_change_form

        if not password_change_form.is_valid():
            messages.error(request, _(u"Passordet ditt ble ikke endret"))
            return render(request, 'profiles/index.html', dict)

        password_change_form.save()
        messages.success(request, _(u"Passordet ditt ble endret"))

    return redirect("profiles")

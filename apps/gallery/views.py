#-*- coding: utf-8 -*-

import os

import json
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.utils.translation import ugettext as _

from apps.gallery.models import UnhandledImage
from apps.gallery.forms import DocumentForm

def _create_request_dictionary(request):

    dict = {
        'unhandled_images': UnhandledImage.objects.all(),
    }
    return dict


def delete_all(request):
    for image in UnhandledImage.objects.all():
        image.delete()
    return redirect('gallery_index')


def index(request):

    request_dict = _create_request_dictionary(request)

    return render(request, 'gallery/index.html', request_dict)


def upload(request):
    return upload_image_temp(request)


def upload_image_temp(request):
# Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():

            unhandled_image = UnhandledImage(image = request.FILES['file'])
            errors = unhandled_image.save()

            if errors:
                return HttpResponse(status=400, content=errors)

            # Redirect to the document list after POST
            return HttpResponse(status=201)
        else:
            error_message = ""

            for field in form.errors:
                error_message += form.errors[field] + "\n"

            return HttpResponse(status=400, content=error_message)
    return HttpResponse(status=405)


def number_of_untreated(request):
    if request.is_ajax():
        if request.method == 'GET':
            return HttpResponse(status=200, content=json.dumps({'untreated': UnhandledImage.objects.all().count()}))
    return HttpResponse(status=405)
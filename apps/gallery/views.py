#-*- coding: utf-8 -*-

import os
import shutil

from django.conf import settings
import json
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.utils.translation import ugettext as _

from apps.gallery.models import UnhandledImage, ResponsiveImage
from apps.gallery.forms import DocumentForm
from apps.gallery import util as galleryUtil

def _create_request_dictionary(request):

    dict = {
        'unhandled_images': UnhandledImage.objects.all(),
    }
    return dict


def delete_all(request):
    for image in UnhandledImage.objects.all():
        image.delete()

    for image in ResponsiveImage.objects.all():
        image.delete()

    return redirect('gallery_index')


def index(request):

    request_dict = _create_request_dictionary(request)

    return render(request, 'gallery/index.html', request_dict)


def upload(request):
    return upload_image_temp(request)

def upload2(request):
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


def upload_image_temp(request):

    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            return _handle_upload(request.FILES['file'])

    return HttpResponse(status=500)


def _handle_upload(uploadedFile):
    unhandled_file_path = galleryUtil.save_unhandled_file(uploadedFile)
    thumbnail_result = galleryUtil.create_thumbnail_for_unhandled_images(unhandled_file_path)

    print "THUMBNAIL RESULT"
    print thumbnail_result

    if thumbnail_result['errors']:
        return HttpResponse(status=500, content=json.dumps(thumbnail_result['error']))

    unhandled_result = UnhandledImage(image = unhandled_file_path, thumbnail = thumbnail_result['thumbnail_path']).save()

    return HttpResponse(status=200)


def number_of_untreated(request):
    if request.is_ajax():
        if request.method == 'GET':
            return HttpResponse(status=200, content=json.dumps({'untreated': UnhandledImage.objects.all().count()}))
    return HttpResponse(status=405)


def get_all_untreated(request):
    if request.is_ajax():
        if request.method == 'GET':

            images = []

            for image in UnhandledImage.objects.all():
                images.append({
                    'id' : image.id,
                    'thumbnail': image.thumbnail.url,
                    'image' : image.image.url
                })

            return HttpResponse(status=200, content=json.dumps({'untreated': images}))
    return HttpResponse(status=405)


def crop_image(request):
    if request.is_ajax():
        if request.method == 'POST':
            cropData = request.POST

            if 'id' not in cropData or 'x' not in cropData or 'y' not in cropData or 'height' not in cropData or 'width' not in cropData:
                return HttpResponse(status=404, content=json.dumps({'error': 'Json must contain id, x, y, height and width.'}))

            image = get_object_or_404(UnhandledImage, pk=cropData['id'])

            copyFrom = image.image.file.name
            copyTo = os.path.join(settings.MEDIA_ROOT, 'images', 'responsive', os.path.basename(image.image.name))
            shutil.copy2(copyFrom, copyTo)

            responsive_image = ResponsiveImage(image_original = copyTo)
            errors = responsive_image.save()
            print image.image.url
            print image.thumbnail.url
            print cropData

            return HttpResponse(status=200, content=json.dumps({'cropData': cropData}))

    return HttpResponse(status=405)
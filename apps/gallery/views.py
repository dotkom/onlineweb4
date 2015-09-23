#-*- coding: utf-8 -*-

import json
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse, HttpResponse

from apps.gallery.models import UnhandledImage, ResponsiveImage
from apps.gallery.forms import DocumentForm
from apps.gallery import util


def _create_request_dictionary(request):

    dictionary = {
        'unhandled_images': UnhandledImage.objects.all(),
        'responsive_images': ResponsiveImage.objects.all(),
    }
    return dictionary


#TODO: Remove this, only for testing
def delete_all(request):
    for image in UnhandledImage.objects.all():
        image.delete()

    for image in ResponsiveImage.objects.all():
        image.delete()

    return redirect('gallery_index')


def index(request):

    request_dict = _create_request_dictionary(request)
    return render(request, "gallery/index.html", request_dict)


def all_images(request):
    """
    Returns a rendered view that displays all images
    uploaded through the gallery app
    """

    template = 'gallery/list.html'
    images = ResponsiveImage.objects.all()

    return render(request, template, {'images': images})


def upload(request):

    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            return _handle_upload(request.FILES['file'])

    return HttpResponse(status=400, content=json.dumps({'success': False, 'message': 'Bad request or invalid type.'}))


# If something goes wrong, all files will have to be deleted, this is not handled now
def _handle_upload(uploaded_file):

    unhandled_file_path = util.save_unhandled_file(uploaded_file)
    thumbnail_result = util.create_thumbnail_for_unhandled_images(unhandled_file_path)

    if 'error' in thumbnail_result:
        #delete files
        return HttpResponse(status=500, content=json.dumps(thumbnail_result['error']))

    # Image objects need to be created with relative paths, create media paths to please django (fuck you, django)
    unhandle_media = util.get_unhandled_media_path(unhandled_file_path)
    unhandled_thumbnail_media = util.get_unhandled_thumbnail_media_path(thumbnail_result['thumbnail_path'])

    #try catch this and delete files on exception
    UnhandledImage(image=unhandle_media, thumbnail=unhandled_thumbnail_media).save()

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
                    'id': image.id,
                    'thumbnail': image.thumbnail.url,
                    'image': image.image.url
                })

            return HttpResponse(status=200, content=json.dumps({'untreated': images}))
    return HttpResponse(status=405)


# Same here, delete all files if something goes wrong, not yet handled
def crop_image(request):
    if request.is_ajax():
        if request.method == 'POST':
            crop_data = request.POST

            if not _verify_crop_data(crop_data):
                return JsonResponse(status=404, data=json.dumps(
                    {'error': 'Json must contain id, x, y, height and width, and name.'}
                ))

            image = get_object_or_404(UnhandledImage, pk=crop_data['id'])
            image_name = crop_data['name']
            responsive_image_path = util.save_responsive_image(image, crop_data)

            # SAMLE ERRORZ PLZ
            util.create_responsive_images(responsive_image_path)

            original_media = util.get_responsive_original_path(responsive_image_path)
            lg_media = util.get_responsive_lg_path(responsive_image_path)
            md_media = util.get_responsive_md_path(responsive_image_path)
            sm_media = util.get_responsive_sm_path(responsive_image_path)
            xs_media = util.get_responsive_xs_path(responsive_image_path)
            thumbnail = util.get_responsive_thumbnail_path(responsive_image_path)

            ResponsiveImage(
                name=image_name,
                image_original=original_media,
                image_lg=lg_media,
                image_md=md_media,
                image_sm=sm_media,
                image_xs=xs_media,
                thumbnail=thumbnail
            ).save()

            image.delete()

            return HttpResponse(status=200, content=json.dumps({'cropData': crop_data}))

    return HttpResponse(status=405)


def _verify_crop_data(crop_data):
    return \
        'id' in crop_data and 'x' in crop_data and 'y' in crop_data and 'height' in crop_data \
        and 'width' in crop_data and 'name' in crop_data


def search(request):
    """
    Performs a search request and returns a JSON response
    :param request: Django Request object
    :return: JsonResponse
    """

    if request.method != 'GET' or 'query' not in request.GET:
        return JsonResponse(status=400, data={'error': 'Bad Request', 'status': 400})

    query = request.GET['query']
    matches = ResponsiveImage.objects.filter(name__icontains=query)

    results = {
        'total': len(matches),
        'images': [{
            'name': image.name,
            'id': image.id,
            'original': settings.MEDIA_URL + str(image.image_original),
            'xs': settings.MEDIA_URL + str(image.image_xs),
            'sm': settings.MEDIA_URL + str(image.image_sm),
            'md': settings.MEDIA_URL + str(image.image_md),
            'lg': settings.MEDIA_URL + str(image.image_lg),
            'timestamp': image.timestamp.strftime('%Y-%M-%DT%H:%m:%s%Z')
        } for image in matches]
    }

    return JsonResponse(data=results, status=200, safe=False)

# -*- coding: utf-8 -*-

import json
import logging

from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse, HttpResponse

from guardian.decorators import permission_required
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from apps.gallery import util
from apps.gallery.models import UnhandledImage, ResponsiveImage
from apps.gallery.forms import DocumentForm
from apps.gallery.serializers import ResponsiveImageSerializer


def _create_request_dictionary(request):

    dictionary = {
        'unhandled_images': UnhandledImage.objects.all(),
        'responsive_images': ResponsiveImage.objects.all(),
    }
    return dictionary


@login_required
@permission_required('gallery.view_responsiveimage')
def all_images(request):
    """
    Returns a rendered view that displays all images
    uploaded through the gallery app
    """

    template = 'gallery/list.html'
    images = ResponsiveImage.objects.all()

    return render(request, template, {'images': images})


@login_required
@permission_required('gallery.add_responsiveimage')
def upload(request):

    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            return _handle_upload(request.FILES['file'])

    return HttpResponse(status=400, content=json.dumps({'success': False, 'message': 'Bad request or invalid type.'}))


# If something goes wrong, all files will have to be deleted, this is not handled now
def _handle_upload(uploaded_file):

    log = logging.getLogger(__name__)
    log.debug('Handling upload of file: %s' % uploaded_file)

    unhandled_file_path = util.save_unhandled_file(uploaded_file)
    log.debug('Unhandled file was saved at: %s' % unhandled_file_path)

    thumbnail_result = util.create_thumbnail_for_unhandled_images(unhandled_file_path)

    if 'error' in thumbnail_result:
        log.error('Error while creating thumbnail for %s' % unhandled_file_path)
        # Delete files
        return HttpResponse(status=500, content=json.dumps(thumbnail_result['error']))

    # Image objects need to be created with relative paths, create media paths to please django (fuck you, django)
    unhandle_media = util.get_unhandled_media_path(unhandled_file_path)
    unhandled_thumbnail_media = util.get_unhandled_thumbnail_media_path(thumbnail_result['thumbnail_path'])

    log.debug('Creating an UnhandledImage for %s' % unhandled_file_path)
    # Try catch this and delete files on exception
    UnhandledImage(image=unhandle_media, thumbnail=unhandled_thumbnail_media).save()

    return HttpResponse(status=200)


@login_required
@permission_required('gallery.add_responsiveimage')
def number_of_untreated(request):
    if request.is_ajax():
        if request.method == 'GET':
            return HttpResponse(status=200, content=json.dumps({'untreated': UnhandledImage.objects.all().count()}))
    return HttpResponse(status=405)


@login_required
@permission_required('gallery.add_responsiveimage')
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
@login_required
@permission_required('gallery.add_responsiveimage')
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
            image_description = crop_data['description']
            responsive_image_path = util.save_responsive_image(image, crop_data)

            # SAMLE ERRORZ PLZ
            util.create_responsive_images(responsive_image_path)

            original_media = util.get_responsive_original_path(responsive_image_path)
            wide_media = util.get_responsive_wide_path(responsive_image_path)
            lg_media = util.get_responsive_lg_path(responsive_image_path)
            md_media = util.get_responsive_md_path(responsive_image_path)
            sm_media = util.get_responsive_sm_path(responsive_image_path)
            xs_media = util.get_responsive_xs_path(responsive_image_path)
            thumbnail = util.get_responsive_thumbnail_path(responsive_image_path)

            ResponsiveImage(
                name=image_name,
                description=image_description,
                image_original=original_media,
                image_lg=lg_media,
                image_md=md_media,
                image_sm=sm_media,
                image_xs=xs_media,
                image_wide=wide_media,
                thumbnail=thumbnail
            ).save()

            image.delete()

            return HttpResponse(status=200, content=json.dumps({'cropData': crop_data}))

    return HttpResponse(status=405)


def _verify_crop_data(crop_data):
    return \
        'id' in crop_data and 'x' in crop_data and 'y' in crop_data and 'height' in crop_data \
        and 'width' in crop_data and 'name' in crop_data


@login_required
@permission_required('gallery.view_responsiveimage')
def search(request):
    """
    Performs a search request and returns a JSON response
    :param request: Django Request object
    :return: JsonResponse
    """

    if request.method != 'GET' or 'query' not in request.GET:
        return JsonResponse(status=400, data={'error': 'Bad Request', 'status': 400})

    query = request.GET['query']

    # Field filters are normally AND'ed together. Q objects circumvent this, treating each field result like a set.
    # This allows us to use set operators like | (union), & (intersect) and ~ (negation)
    matches = ResponsiveImage.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))[:10]

    results = {
        'total': len(matches),
        'images': [{
            'name': image.name,
            'description': image.description,
            'id': image.id,
            'original': settings.MEDIA_URL + str(image.image_original),
            'thumbnail': settings.MEDIA_URL + str(image.thumbnail),
            'wide': settings.MEDIA_URL + str(image.image_wide),
            'xs': settings.MEDIA_URL + str(image.image_xs),
            'sm': settings.MEDIA_URL + str(image.image_sm),
            'md': settings.MEDIA_URL + str(image.image_md),
            'lg': settings.MEDIA_URL + str(image.image_lg),
            'timestamp': image.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for image in matches]
    }

    return JsonResponse(data=results, status=200, safe=False)


# REST Framework

class ResponsiveImageViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    """
    Image viewset. Can be filtered on 'year', 'month', and free text search using 'query'.

    The 'query' filter performs a case-insensitive OR match on either image name or description.
    """

    queryset = ResponsiveImage.objects.filter().order_by('-timestamp')
    serializer_class = ResponsiveImageSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = self.queryset
        month = self.request.query_params.get('month', None)
        year = self.request.query_params.get('year', None)
        query = self.request.query_params.get('query', None)

        if year:
            if month:
                # Filtering on year and month
                queryset = queryset.filter(
                    timestamp__year=year,
                    timestamp__month=month,
                ).order_by('-timestamp')
            else:
                # Filtering only on year
                queryset = queryset.filter(
                    timestamp__year=year,
                ).order_by('-timestamp')

        if query:
            # Restrict results based off of search
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))

        return queryset

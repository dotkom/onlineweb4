# -*- coding: utf8 -*-

from logging import getLogger

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect

from django.views.generic import DetailView, ListView, TemplateView, UpdateView, FormView, CreateView
from django.views.generic.edit import FormMixin

from apps.photoalbum.dashboard.forms import AlbumForm
from apps.photoalbum.models import Album
from apps.dashboard.tools import DashboardPermissionMixin, get_base_context, check_access_or_403
from apps.photoalbum.utils import get_photos_from_form, get_photos_to_album
from apps.gallery.models import ResponsiveImage

# @permission_required('photoalbum.view_album')
def photoalbum_index(request):
	# check_access_or_403(request)

	context = get_base_context(request)
	context['albums'] = Album.objects.all()

	return render(request, 'photoalbum/dashboard/index.html', context)


# @permission_required('photoalbum.add_album')
def photoalbum_create(request):
	# check_access_or_403(request)

	form = AlbumForm()

	if request.method == 'POST':

		if 'upload_photos' in request.POST:
			photos = form['files']
			print("Files: ", photos)

		form = AlbumForm(request.POST)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.save()
			instance.changed_by = request.user
			instance.created_by = request.user
			photos = get_photos_to_album(instance.title)
						
			for photo in photos:
				instance.photos.add(photo)

			instance.save()

			messages.success(request, 'Albumet ble opprettet.')
			
			return redirect(photoalbum_detail, pk=instance.pk)
		else:
			message.error(request, 'Noen av de påkrevde feltene inneholder feil.')

	context = get_base_context(request)
	context['form'] = form

	return render(request, 'photoalbum/dashboard/create.html', context)

def upload_photos(request, album_title):
	print("In upload_photos")
	photos = form['files']
	print("Files: ", photos)

#@permissionrequired('photoalbum.view_album')
def photoalbum_detail(request, pk):
	#check_access_or_403(request)

	album = get_object_or_404(Album, pk=pk)

	context = get_base_context(request)
	context['album'] = album

	return render(request, 'photoalbum/dashboard/detail.html', context)


#@permissionrequired('photoalbum.change_album')
def photoalbum_edit(request, pk):
	#check_access_or_403(request)

	album = get_object_or_404(Album, pk=pk)

	form = AlbumForm(instance=album)

	if request.method == 'POST':
		if 'upload_photos' in request.POST:
			upload_photos(form)

		if 'action' in request.POST and request.POST['action'] == 'delete':
			instance = get_object_or_404(Album, pk=album.pk)
			album_title = instance.title
			album_pk = instance.pk
			instance.delete()
			messages.success(request, '%s ble slettet.' % album_title)
			getLogger(__name__).info('%s deleted album %d (%s)' % (request.user, album_pk, album_title))

			return redirect(photoalbum_index)

		form = AlbumForm(request.POST)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.save()
			instance.changed_by = request.user
			instance.created_by = request.user
			photos = get_photos_to_album(instance.title)
			
			for photo in photos:
				instance.photos.add(photo)

			instance.save()

			messages.success(request, 'Albumet ble lagret.')
			getLogger(__name__).info('%s edited album %d (%s)' % (request.user, instance.pk, instance.title))
			
			return redirect(photoalbum_index)
		else:
			message.error(request, 'Noen av de påkrevde feltene inneholder feil.')

	context = get_base_context(request)
	context['form'] = form
	context['edit'] = True

	return render(request, 'photoalbum/dashboard/create.html', context)

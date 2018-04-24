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
from apps.photoalbum.utils import get_photos_from_form
from apps.gallery.models import ResponsiveImage


def photoalbum_index(request):
	# check_access_or_403(request)

	context = get_base_context(request)
	context['albums'] = Album.objects.all()

	return render(request, 'photoalbum/dashboard/index.html', context)

def photoalbum_create(request):

	form = AlbumForm()

	if request.method == 'POST':
		form = AlbumForm(request.POST)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.save()
			instance.changed_by = request.user
			instance.created_by = request.user
			instance.photos.add(ResponsiveImage.objects.get(pk=2))
			instance.save()

			messages.success(request, 'Albumet ble opprettet.')
			#getLogger(__name__).info('%s deleted album %d (%s)' % (request.user, instance.pk, instance.title))
			
			return redirect(photoalbum_detail, pk=instance.pk)
		else:
			message.error(request, 'Noen av de påkrevde feltene inneholder feil.')

	context = get_base_context(request)
	context['form'] = form

	return render(request, 'photoalbum/dashboard/create.html', context)


#@permission_required('photoalbum.view_photoalbum')
class PhotoAlbumDetailDashboard(DashboardPermissionMixin, DetailView):
	print("In PhotoAlbumDetailDashboard")
	permission_required = 'superuser'

	model = Album
	template_name = 'photoalbum/dashboard/detail.html'

	def form_valid(self, form):

		messages.success(self.request, 'PhotoAlbum ble oppdatert.')
		#getLogger(__name__).info('%s updated PhotoAlbum %d' & (self.request.user, self.request.object.id))

		return super(PhotoAlbumDetail, self).form_valid(form)

	def form_invalid(self, form):

		messages.error(self.request, 'Noen av feltene inneholder feil.')

		return super(PhotoAlbumDetail, self).form_invalid(form)

	def get_success_url(self):

		return reverse('dashboard_photoalbum_detail', kwargs={'pk': self.object.id})

	def get_context_data(self, **kwargs):
		print("In get context data")
		context = super(PhotoAlbumDetailDashboard, self).get_context_data(**kwargs)
		album = get_object_or_404(Album, pk=self.kwargs.get('pk'))
		
		context['album'] = album

		print("Photos to album in detail")
		#album.photos.add(ResponsiveImage.objects.get(pk=1))
		#print(album.photos.all())

		return context
	
def photoalbum_detail(request, pk):
	#check_access_or_403(request)

	album = get_object_or_404(Album, pk=pk)

	context = get_base_context(request)
	context['album'] = album

	return render(request, 'photoalbum/dashboard/detail.html', context)


def photoalbum_edit(request, pk):
	#check_access_or_403(request)

	album = get_object_or_404(Album, pk=pk)

	form = AlbumForm(instance=album)

	if request.method == 'POST':

		if 'action' in request.POST and request.POST['action'] == 'delete':
			instance = get_object_or_404(Album, pk=album.pk)
			album_title = instance.title
			album_pk = instance.pk
			instance.delete()
			messages.success(request, '%s ble slettet.' % album_title)
			getLogger(__name__).info('%s deleted album %d (%s)' % (request.user, album_pk, album_title))

			return redirect('dashboard_photoalbum_index')

		form = AlbumForm(request.POST)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.save()
			instance.changed_by = request.user
			instance.created_by = request.user
			instance.photos.add(ResponsiveImage.objects.get(pk=2))
			instance.save()

			messages.success(request, '%s ble slettet.' % instance.title)
			getLogger(__name__).info('%s deleted album %d (%s)' % (request.user, instance.pk, instance.title))
			
			return redirect('dashboard_photoalbum_index')
		else:
			message.error(request, 'Noen av de påkrevde feltene inneholder feil.')

	context = get_base_context(request)
	context['form'] = form
	context['edit'] = True

	return render(request, 'photoalbum/dashboard/create.html', context)

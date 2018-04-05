# -*- coding: utf8 -*-
from logging import getLogger

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render

from django.views.generic import DetailView, ListView, TemplateView, UpdateView, FormView, CreateView


from apps.photoalbum.dashboard.forms import AlbumForm
from apps.photoalbum.models import Album
from apps.dashboard.tools import DashboardPermissionMixin



#@permission_required('photoalbum.view_photoalbum')
class PhotoAlbumIndex(DashboardPermissionMixin, ListView):
	permission_required = 'superuser'

	albums = Album.objects.all()
	for album in albums: 
		print(album.title)


	model = Album
	template_name = 'photoalbum/dashboard/index.html'
	queryset = Album.objects.all().order_by('-timestamp')[:15]

	print(Album.objects.all())

	def get_context_data(self, **kwargs):
		context = super(PhotoAlbumIndex, self).get_context_data(**kwargs) 

		context['albums'] = Album.objects.all()
		return context


#@permission_required('photoalbum.view_photoalbum')
class PhotoAlbumCreate(DashboardPermissionMixin, CreateView):
	permission_required = 'superuser'

	model = Album
	template_name = 'photoalbum/dashboard/create.html'
	form_class = AlbumForm
	context_object_name = 'album'
	form = AlbumForm()

	#def post(self, request, *args, **kwargs):
		#form = AlbumForm(request.POST, request.FILES)
		#print("In post")

	def form_valid(self, form):
		print("Form valid: ", form)
		instance = form.save(commit=False)
		print(instance)
		#form.save_m2m()

		messages.success(self.request, 'PhotoAlbum ble laget.')
		#getLogger(__name__).info('%s created PhotoAlbum %d' & (self.request.user, self.request.object.id))

		print("Before return redirect")
		#return reverse('dashboard_photoalbum_detail', kwargs={'album_pk': instance.pk})

		return super(PhotoAlbumCreate, self).form_valid(form)
		#return super(PhotoAlbumCreate, self).get_success_url()

	def form_invalid(self, form):
		print("Form invalid")

		messages.error(self.request, 'Noen av feltene inneholder feil.')

		return super(PhotoAlbumCreate, self).form_invalid(form)

	def get_success_url(self):
		print("Success url")
		print(self.object)
		return reverse('dashboard_photoalbum_detail', kwargs={'pk': self.object.pk})


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
	



class PhotoAlbumEdit(DashboardPermissionMixin, UpdateView):

	form_class = AlbumForm
	model = Album
	context_object_name = 'album'
	permission_required = 'superuser'
	template_name = 'photoalbum/dashboard/create.html'

	def get_success_url(self):
		return reverse('dashboard_photoalbum_detail', kwargs={'pk': self.kwargs.get('album_pk')})

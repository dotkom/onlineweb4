# -*- coding: utf8 -*-

from django.contrib import messages
from django.views.generic import DetailView, ListView, TemplateView, UpdateView, FormView


from apps.photoalbum.dashboard.forms import AlbumForm
from apps.photoalbum.models import Album
from apps.dashboard.tools import DashboardPermissionMixin



#@permission_required('photoalbum.view_photoalbum')
class PhotoAlbumIndex(DashboardPermissionMixin, ListView):
	

	model = Album
	template_name = 'photoalbum/index.html'

	def get(self, request, *args, **kwargs):
		filter = AlbumFilter(request.GET, queryset=Album.objects.all())
		prokom = is_prokom(request.user)


		return render(request, 'photoalbum/index.html')

#@permission_required('photoalbum.view_photoalbum')
class PhotoAlbumCreate(TemplateView, FormView):

	model = Album
	template_name = 'photoalbum/dashboard/create.html'
	context_object_name = 'photoalbum'
	form_class = AlbumForm
	form = AlbumForm()

	def post(self, request, *args, **kwargs):
		form = AlbumForm(request.POST, request.FILES)
		print("In post")

	def form_valid(self, form):
		message.success(self.request, 'PhotoAlbum ble laget.')
		getLogger(__name__).info('%s created PhotoAlbum %d' & (self.request.user, self.request.object.id))

		return super(PhotoAlbumCreate, self).form_valid(form)

	def form_invalid(self, form):

		message.error(self.request, 'Noen av feltene inneholder feil.')

		return super(PhotoAlbumCreate, self).form_invalid(form)

	def get_success_url(self):

		return reverse('dashboard_photoalbum_detail', kwargs={'pk': self.object.id})


#@permission_required('photoalbum.view_photoalbum')
class PhotoAlbumDetail(DashboardPermissionMixin, UpdateView):

	def form_valid(self, form):

		message.success(self.request, 'PhotoAlbum ble oppdatert.')
		getLogger(__name__).info('%s updated PhotoAlbum %d' & (self.request.user, self.request.object.id))

		return super(PhotoAlbumDetail, self).form_valid(form)

	def form_invalid(self, form):

		message.error(self.request, 'Noen av feltene inneholder feil.')

		return super(PhotoAlbumDetail, self).form_invalid(form)

	def get_success_url(self):

		return reverse('dashboard_photoalbum_detail', kwargs={'pk': self.object.id})



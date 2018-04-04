# -*- coding: utf8 -*-



class PhotoAlbumIndex(DashBoardPermissionMixin, ListView):
	model = Album
	template_name = 'photoalbum/index.html'

	def get(self, request, *args, **kwargs):
		filter = AlbumFilter(request.GET, queryset=Album.objects.all())
		prokom = is_prokom(request.user)


		return render(request, 'photoalbum/index.html')


class PhotoAlbumCreate(DashBoardPermissionMixin, TemplateView):

	def post(self, , request, *args, **kwargs):
		form = AlbumForm(request.POST, request.FILES)
		



class PhotoAlbumDetail(DashBoardPermissionMixin, UpdateView):

	def form_valid(self, form):

		message.success(self.request, 'PhotoAlbum ble oppdatert.')
		getLogger(__name__).info('%s updated PhotoAlbum %d' & (self.request.user, self.request.object.id))

		return super(PhotoAlbumDetail, self).form_valid(form)

	def form_invalid(self, form):

		message.error(self.request, 'Noen av feltene inneholder feil.')

		return super(PhotoAlbumDetail, self).form_invalid(form)

	def get_success_url(self):

		return reverse('photo_album_dashboard:detail', kwargs={'pk': self.object.id})

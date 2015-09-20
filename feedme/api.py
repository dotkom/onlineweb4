from django.conf.urls import url
from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.utils import trailing_slash
from feedme.models import Poll, Restaurant, Answer, Order, OrderLine

class RestaurantResource(ModelResource):
    class Meta:
        queryset = Restaurant.objects.all()
        resource_name = 'restaurant'

class VoteResource(ModelResource):
    restaurant = fields.ToOneField(RestaurantResource, 'answer', full=True, null=True)
    class Meta:
        queryset = Answer.objects.all()
        resource_name = 'vote'

class PollResource(ModelResource):
    votes = fields.ToManyField(VoteResource, 'votes', full=True, null=True)
    class Meta:
        queryset = Poll.objects.all()
        resource_name = 'poll'

    def prepend_urls(self):
        """ Adds the following urls to the base resoucre """
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/winner%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('winner'), name="api_poll_winner")
        ]

    def winner(self, request, **kwargs):
        """ proxy for the poll winner method """

        self.method_check(request, allowed=['get'])

        # Bundle for the method
        basic_bundle = self.build_bundle(request=request)

        poll = self.cached_obj_get(bundle=basic_bundle, **self.remove_api_resource_names(kwargs))

        return self.create_response(request, poll.get_winner())

class OrderResource(ModelResource):
    class Meta:
        queryset = Order.objects.all()
        resource_name = 'order'

class OrderLineResource(ModelResource):
    order = fields.ForeignKey(OrderResource, 'order')
    class Meta:
        queryset = OrderLine.objects.all()
        resource_name = 'orderline'

# Todo - Need some kind of auth?
#class BalanceResource(ModelResource):

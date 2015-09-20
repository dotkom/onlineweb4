from django.conf.urls import patterns, include, url

# API
from tastypie.api import Api
from feedme.api import PollResource, RestaurantResource, VoteResource, OrderResource, OrderLineResource

v1_api = Api(api_name='v1')
v1_api.register(PollResource())
v1_api.register(RestaurantResource())
v1_api.register(VoteResource())
v1_api.register(OrderResource())
v1_api.register(OrderLineResource())

urlpatterns = patterns(
    'feedme.views',
    url(r'^$', 'index', name='feedme_index'),
    url(r'^neworder/$', 'orderlineview', name='new_orderline'),
    url(r'^edit/(?P<orderline_id>\d+)/$', 'edit_orderline', name='edit_orderline'),
    url(r'^delete/(?P<orderline_id>\d+)/$', 'delete_orderline', name='delete_orderline'),
    url(r'^order/$', 'orderview', name='new_order'),
    # url(r'^order/(?P<order_id>\d+)/$', 'edit_order', name='edit_order'),
    # url(r'^delete/order/(?P<order_id>\d+)/$','delete_order', name='delete_order'),
    url(r'^join/(?P<orderline_id>\d+)/$', 'join_orderline', name='join_orderline'),
    url(r'^leave/(?P<orderline_id>\d+)/$', 'leave_orderline', name='leave_orderline'),
    url(r'^admin/$', 'new_order', name='admin'),
    url(r'^admin/neworder/$', 'new_order', name='new_order'),
    url(r'^admin/orders/$', 'manage_order', name='manage_order'),
    url(r'^admin/users/$', 'manage_users', name='manage_users'),
    url(r'^admin/orderlimit/$', 'set_order_limit', name='set_order_limit'),
    url(r'^admin/newrestaurant/$', 'new_restaurant', name='new_restaurant'),
    url(r'^admin/newpoll/$', 'new_poll', name='new_poll'),

    url(r'api/', include(v1_api.urls)),
)

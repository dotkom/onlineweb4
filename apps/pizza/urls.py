from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.pizza.views',
    # Home
    url(r'^$', 'pizza_index', name='pizza_index'),
    url(r'^new/$', 'pizza_new', name='pizza_new'),
    url(r'^edit/(?P<pizza_id>\d+)/$','pizza_edit', name='pizza_edit'),
    url(r'^delete/(?P<pizza_id>\d+)/$','pizza_delete', name='pizza_delete'),
    url(r'^join/(?P<pizza_id>\d+)/$','pizza_join', name='pizza_join'),

    # Order
    url(r'^order/$', 'pizza_new_order', name='pizza_order_new'),
    url(r'^order/(?P<order_id>\d+)/$', 'pizza_order_edit', name='pizza_order_edit'),
    url(r'^order/(?P<order_id>\d+)/delete/$','pizza_order_delete', name='pizza_order_delete'),
    
    # Admin
    url(r'^admin/$', 'pizza_admin_new', name='pizza_admin'),
    url(r'^admin/new/$', 'pizza_admin_new', name='pizza_admin_new'),
    url(r'^admin/orders/$', 'pizza_admin_orders', name='pizza_admin_orders'),
    url(r'^admin/users/$', 'pizza_admin_users', name='pizza_admin_users'),
    url(r'^admin/limit/$', 'pizza_admin_limit', name='pizza_admin_limit'),
)

from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.pizza.views',
    url(r'^$', 'index', name='index'),
    url(r'^newpizza/$', 'pizzaview', name='new_pizza'),
    url(r'^edit/(?P<pizza_id>\d+)/$','edit_pizza', name='edit_pizza'),
    url(r'^delete/(?P<pizza_id>\d+)/$','delete_pizza', name='delete_pizza'),
    url(r'^order/$', 'orderview', name='new_order'),
    url(r'^order/(?P<order_id>\d+)/$', 'edit_order', name='edit_order'),
    url(r'^delete/order/(?P<order_id>\d+)/$','delete_order', name='delete_order'),
    url(r'^join/(?P<pizza_id>\d+)/$','join_pizza', name='join_pizza'),
    url(r'^admin/$', 'new_order_line', name='admin'),
    url(r'^admin/neworder/$', 'new_order_line', name='new_order_line'),
    url(r'^admin/orders/$', 'manage_order_lines', name='manage_order_lines'),
    url(r'^admin/users/$', 'manage_users', name='manage_users'),
    url(r'^admin/orderlimit/$', 'set_order_limit', name='set_order_limit'),
)

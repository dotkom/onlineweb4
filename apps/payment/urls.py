# -*- coding: utf-8 -*-
from django.conf.urls import url

from apps.api.utils import SharedAPIRootRouter
from apps.payment import views

urlpatterns = [
    url(r'^$', views.payment, name='payment'),
    url(r'^payment_info/$', views.payment_info, name='payment_info'),
    url(r'^refund/(?P<payment_relation_id>\d+)$', views.payment_refund, name='payment_refund'),
    url(r'^saldo_info/$', views.saldo_info, name='saldo_info'),
    url(r'^saldo/$', views.saldo, name='saldo'),
    url(r'^webshop_info/$', views.webshop_info, name='webshop_info'),
    url(r'^webshop_pay/$', views.webshop_pay, name='webshop_pay'),
    url(r'^refund/(?P<payment_relation_id>\d+)$', views.payment_refund, name='payment_refund'),
]

# API v1
router = SharedAPIRootRouter()
router.register('payment/relations', views.PaymentRelationCreateViewSet, base_name='payment_relations')
router.register('payment/transactions', views.PaymentTransactionCreateViewSet, base_name='payment_transactions')

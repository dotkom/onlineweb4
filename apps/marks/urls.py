# -*- coding: utf-8 -*-
from apps.api.utils import SharedAPIRootRouter
from apps.marks import views

urlpatterns = []

# API v1
router = SharedAPIRootRouter()
router.register('marks/rule-sets', views.MarkRuleSetViewSet, basename='mark_rule_sets')
router.register('marks/acceptance', views.RuleAccpetanceViewSet, basename='mark_rule_acceptance')

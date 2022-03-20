# -*- coding: utf-8 -*-
from django.urls import re_path

from apps.api.utils import SharedAPIRootRouter
from apps.feedback import views

base_url = (
    r"^(?P<applabel>\w+)/(?P<appmodel>\w+)/(?P<object_id>\d+)/(?P<feedback_id>\d+)/"
)

urlpatterns = [
    re_path("^$", views.index, name="feedback_index"),
    re_path(base_url + r"$", views.feedback, name="feedback"),
    re_path(base_url + r"results/$", views.result, name="result"),
    re_path(base_url + r"results/chartdata/$", views.chart_data, name="chart_data"),
    re_path(
        base_url + r"results/(?P<token>(\w|\-)+)/$",
        views.results_token,
        name="results_token",
    ),
    re_path(
        base_url + r"results/(?P<token>(\w|\-)+)/chartdata/$",
        views.chart_data_token,
        name="chart_data_token",
    ),
    re_path("^deleteanswer/$", views.delete_answer, name="delete_anwer"),
]


# API v1
router = SharedAPIRootRouter()
router.register(
    prefix="feedback/generic-surveys",
    viewset=views.GenericSurveyViewSet,
    basename="feedback_generic_surveys",
)
router.register(
    prefix="feedback/templates",
    viewset=views.FeedbackTemplateViewSet,
    basename="feedback_templates",
)
router.register(
    prefix="feedback/relations",
    viewset=views.FeedbackRelationViewSet,
    basename="feedback_relations",
)
router.register(
    prefix="feedback/results-auth",
    viewset=views.FeedbackResultsViewSet,
    basename="feedback_results",
)
router.register(
    prefix="feedback/results-token",
    viewset=views.FeedbackTokenResultsViewSet,
    basename="feedback_results_token",
)
router.register(
    prefix="feedback/questions/text",
    viewset=views.TextQuestionViewSet,
    basename="feedback_question_text",
)
router.register(
    prefix="feedback/questions/rating",
    viewset=views.RatingQuestionViewSet,
    basename="feedback_question_rating",
)
router.register(
    prefix="feedback/questions/multiple-choice-objects",
    viewset=views.MultipleChoiceQuestionViewSet,
    basename="feedback_question_multiple_choice",
)
router.register(
    prefix="feedback/questions/multiple-choice-relations",
    viewset=views.MultipleChoiceRelationViewSet,
    basename="feedback_question_multiple_choice_relation",
)

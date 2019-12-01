import logging

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from rest_framework import status

from apps.authentication.models import OnlineUser as User
from apps.feedback.models import (
    Choice,
    Feedback,
    FeedbackRelation,
    GenericSurvey,
    MultipleChoiceQuestion,
    MultipleChoiceRelation,
    RatingQuestion,
    TextQuestion,
)
from apps.online_oidc_provider.test import OIDCTestCase

from .base_tests import FeedbackTestCaseMixin

logger = logging.getLogger(__name__)


def add_content_type_permission_to_group(group: Group, model):
    content_type = ContentType.objects.get_for_model(model)
    all_permissions = Permission.objects.filter(content_type=content_type)
    for permission in all_permissions:
        print(permission.codename)
        group.permissions.add(permission)


class FeedbackAPITestCase(FeedbackTestCaseMixin, OIDCTestCase):
    url_basename = None

    def setUp(self):
        super().setUp()

        self.feedback: Feedback = G(Feedback)

    def get_list_url(self):
        return reverse(f"{self.url_basename}-list")

    def get_detail_url(self, obj):
        return reverse(f"{self.url_basename}-detail", args=[obj.id])

    def create_feedback_relation(self, *args, **kwargs):
        return super().create_feedback_relation(feedback=self.feedback, *args, **kwargs)

    def create_generic_survey(self, **kwargs):
        survey: GenericSurvey = G(
            GenericSurvey,
            feedback=self.feedback,
            deadline=(timezone.now() + timezone.timedelta(days=2)).date(),
            **kwargs,
        )

        return survey

    def create_text_question(self) -> TextQuestion:
        return G(TextQuestion, feedback=self.feedback)

    def create_rating_question(self) -> RatingQuestion:
        return G(RatingQuestion, feedback=self.feedback)

    def create_multiple_choice_question(self) -> MultipleChoiceQuestion:
        multiple_choice_question: MultipleChoiceQuestion = G(MultipleChoiceQuestion)
        G(Choice, question=multiple_choice_question)
        G(Choice, question=multiple_choice_question)
        G(
            MultipleChoiceRelation,
            question=multiple_choice_question,
            feedback=self.feedback,
        )
        return multiple_choice_question


class FeedbackRelationTest(FeedbackAPITestCase):
    url_basename = "feedback_relations"

    def get_submit_url(self, relation: FeedbackRelation):
        return reverse(f"{self.url_basename}-submit", args=[relation.id])

    def test_url_returns_403_without_login(self):
        response = self.client.get(self.get_list_url(), **self.bare_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_url_returns_ok_with_login(self):
        response = self.client.get(self.get_list_url(), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_retrieve_a_relation_when_they_cannot_answer(self):
        relation = self.create_feedback_relation()
        response = self.client.get(self.get_detail_url(relation), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_retrieve_a_relation_when_they_can_answer(self):
        relation = self.create_feedback_relation(user=self.user)
        response = self.client.get(self.get_detail_url(relation), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_retrieve_a_relation_when_they_have_answered(self):
        relation = self.create_feedback_relation()
        relation.answered.add(self.user)
        response = self.client.get(self.get_detail_url(relation), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_users_can_answer_with_a_rating_question(self):
        rating_question = self.create_rating_question()
        relation = self.create_feedback_relation(user=self.user)
        response = self.client.post(
            self.get_submit_url(relation),
            {"rating_answers": [{"question": rating_question.id, "answer": 1}]},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_answer_with_a_rating_question_with_an_invalid_value(self):
        rating_question = self.create_rating_question()
        relation = self.create_feedback_relation(user=self.user)
        response = self.client.post(
            self.get_submit_url(relation),
            {"rating_answers": [{"question": rating_question.id, "answer": 7}]},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_answer_with_a_text_question(self):
        question = self.create_text_question()
        relation = self.create_feedback_relation(user=self.user)
        response = self.client.post(
            self.get_submit_url(relation),
            {"text_answers": [{"question": question.id, "answer": "Dette er et svar"}]},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_answer_with_a_text_question_with_an_invalid_value(self):
        question = self.create_text_question()
        relation = self.create_feedback_relation(user=self.user)
        response = self.client.post(
            self.get_submit_url(relation),
            {"text_answers": [{"question": question.id, "answer": ""}]},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_answer_with_a_multiple_choice_question(self):
        question = self.create_multiple_choice_question()
        relation = self.create_feedback_relation(user=self.user)
        response = self.client.post(
            self.get_submit_url(relation),
            {
                "multiple_choice_answers": [
                    {"question": question.id, "answer": question.choices.first().choice}
                ]
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_answer_with_a_multiple_choice_question_with_an_invalid_value(self):
        question = self.create_multiple_choice_question()
        relation = self.create_feedback_relation(user=self.user)
        response = self.client.post(
            self.get_submit_url(relation),
            {
                "multiple_choice_answers": [
                    {
                        "question": question.id,
                        "answer": question.choices.first().choice + " something extra",
                    }
                ]
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_users_can_answer_with_all_types(self):
        text_question = self.create_text_question()
        rating_question = self.create_rating_question()
        multiple_choice_question = self.create_multiple_choice_question()
        relation = self.create_feedback_relation(user=self.user)
        response = self.client.post(
            self.get_submit_url(relation),
            {
                "rating_answers": [{"question": rating_question.id, "answer": 1}],
                "text_answers": [
                    {"question": text_question.id, "answer": "Dette er et svar"}
                ],
                "multiple_choice_answers": [
                    {
                        "question": multiple_choice_question.id,
                        "answer": multiple_choice_question.choices.first().choice,
                    }
                ],
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(relation.text_answers.count(), 1)
        self.assertEqual(relation.rating_answers.count(), 1)
        self.assertEqual(relation.multiple_choice_answers.count(), 1)

    def test_users_cannot_answer_without_filling_all_fields(self):
        rating_question = self.create_rating_question()
        self.create_text_question()
        relation = self.create_feedback_relation(user=self.user)
        response = self.client.post(
            self.get_submit_url(relation),
            {"rating_answers": [{"question": rating_question.id, "answer": 1}]},
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_users_cannot_answer_when_filling_too_many_fields(self):
        rating_question = self.create_rating_question()
        relation = self.create_feedback_relation(user=self.user)
        response = self.client.post(
            self.get_submit_url(relation),
            {
                "rating_answers": [
                    {"question": rating_question.id, "answer": 1},
                    {"question": rating_question.id, "answer": 2},
                ]
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_allowed_users_can_answer_generic_survey(self):
        question = self.create_text_question()
        survey = self.create_generic_survey(allowed_users=[self.user])
        response = self.client.post(
            self.get_submit_url(survey.get_feedback_relation()),
            {"text_answers": [{"question": question.id, "answer": "Dette er et svar"}]},
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_answer_generic_survey_without_being_allowed(self):
        question = self.create_text_question()
        survey = self.create_generic_survey(allowed_users=[G(User)])
        response = self.client.post(
            self.get_submit_url(survey.get_feedback_relation()),
            {"text_answers": [{"question": question.id, "answer": "Dette er et svar"}]},
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_answer_generic_survey_when_no_allowed_users_are_defined(self):
        question = self.create_text_question()
        survey = self.create_generic_survey(allowed_users=[])
        response = self.client.post(
            self.get_submit_url(survey.get_feedback_relation()),
            {"text_answers": [{"question": question.id, "answer": "Dette er et svar"}]},
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TextQuestionTestCase(FeedbackAPITestCase, OIDCTestCase):
    url_basename = "feedback_question_text"

    def setUp(self):
        super().setUp()
        self.group: Group = G(Group)
        add_content_type_permission_to_group(self.group, TextQuestion)
        self.user.is_superuser = False
        self.user.save()

        self.feedback_relation = self.create_feedback_relation(user=self.user)

    def test_cannot_view_without_login(self):
        response = self.client.get(self.get_list_url(), **self.bare_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_view_without_permission(self):
        response = self.client.get(self.get_list_url(), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_questions(self):
        self.group.user_set.add(self.user)
        response = self.client.get(self.get_list_url(), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_can_retrieve_questions(self):
        self.group.user_set.add(self.user)
        question = self.create_text_question()
        response = self.client.get(self.get_detail_url(question), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_create_question(self):
        response = self.client.post(
            self.get_list_url(),
            {
                "feedback": self.feedback.feedback_id,
                "order": 10,
                "label": "this is a label",
                "display": True,
            },
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permitted_user_can_create_question(self):
        self.group.user_set.add(self.user)
        response = self.client.post(
            self.get_list_url(),
            {
                "feedback": self.feedback.feedback_id,
                "order": 10,
                "label": "this is a label",
                "display": True,
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_permitted_user_can_update_question(self):
        self.group.user_set.add(self.user)
        question = self.create_text_question()
        response = self.client.patch(
            self.get_detail_url(question), {"display": False}, **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("display"), False)

    def test_permitted_user_can_delete_question(self):
        self.group.user_set.add(self.user)
        question = self.create_text_question()
        response = self.client.delete(self.get_detail_url(question), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TextQuestion.objects.filter(pk=question.id).count(), 0)


class RatingQuestionTestCase(FeedbackAPITestCase, OIDCTestCase):
    url_basename = "feedback_question_rating"

    def setUp(self):
        super().setUp()
        self.group: Group = G(Group)
        add_content_type_permission_to_group(self.group, RatingQuestion)

        self.feedback_relation = self.create_feedback_relation(user=self.user)

    def test_cannot_view_without_login(self):
        response = self.client.get(self.get_list_url(), **self.bare_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_questions(self):
        self.group.user_set.add(self.user)
        response = self.client.get(self.get_list_url(), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_retrieve_without_permission(self):
        question = self.create_rating_question()
        response = self.client.get(self.get_detail_url(question), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_retrieve_questions(self):
        self.group.user_set.add(self.user)
        question = self.create_rating_question()
        response = self.client.get(self.get_detail_url(question), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_create_question(self):
        response = self.client.post(
            self.get_list_url(),
            {
                "feedback": self.feedback.feedback_id,
                "order": 10,
                "label": "this is a label",
                "display": True,
            },
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permitted_user_can_create_question(self):
        self.group.user_set.add(self.user)
        response = self.client.post(
            self.get_list_url(),
            {
                "feedback": self.feedback.feedback_id,
                "order": 10,
                "label": "this is a label",
                "display": True,
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_permitted_user_can_update_question(self):
        self.group.user_set.add(self.user)
        question = self.create_rating_question()
        response = self.client.patch(
            self.get_detail_url(question), {"display": False}, **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("display"), False)

    def test_permitted_user_can_delete_question(self):
        self.group.user_set.add(self.user)
        question = self.create_rating_question()
        response = self.client.delete(self.get_detail_url(question), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RatingQuestion.objects.filter(pk=question.id).count(), 0)


class GenericSurveyTestCase(OIDCTestCase):
    url_basename = "feedback_generic_surveys"

    def setUp(self):
        super().setUp()
        self.group: Group = G(Group)
        add_content_type_permission_to_group(self.group, GenericSurvey)
        self.feedback: Feedback = G(Feedback)

    def get_list_url(self):
        return reverse(f"{self.url_basename}-list")

    def get_detail_url(self, obj: GenericSurvey):
        return reverse(f"{self.url_basename}-detail", args=[obj.id])

    def create_survey(self, owner: User = None, owner_group: Group = None):
        survey: GenericSurvey = G(
            GenericSurvey,
            feedback=self.feedback,
            owner=owner if owner else self.user,
            owner_group=owner_group if owner_group else self.group,
        )
        return survey

    def test_cannot_view_without_login(self):
        response = self.client.get(self.get_list_url(), **self.bare_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_view_without_permission(self):
        response = self.client.get(self.get_list_url(), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permitted_can_list_surveys(self):
        self.group.user_set.add(self.user)
        response = self.client.get(self.get_list_url(), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_user_can_retrieve_their_own_survey(self):
        self.group.user_set.add(self.user)
        survey = self.create_survey()
        response = self.client.get(self.get_detail_url(survey), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_user_cannot_retrieve_survey_without_ownership(self):
        self.group.user_set.add(self.user)
        survey = self.create_survey(G(User), G(Group))
        response = self.client.get(self.get_detail_url(survey), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        survey.owner_group = self.group
        survey.save()

        response = self.client.get(self.get_detail_url(survey), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_create_survey(self):
        self.group.user_set.add(self.user)
        survey_data = {
            "title": "The very best survey",
            "feedback": self.feedback.id,
            "deadline": (timezone.datetime.now() + timezone.timedelta(days=7)).date(),
        }
        response = self.client.post(self.get_list_url(), survey_data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_update_survey(self):
        self.group.user_set.add(self.user)
        survey = self.create_survey()
        survey_data = {
            "deadline": (timezone.datetime.now() + timezone.timedelta(days=14)).date()
        }

        response = self.client.patch(
            self.get_detail_url(survey), survey_data, **self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_updating_survey_does_not_change_owner(self):
        self.group.user_set.add(self.user)
        survey = self.create_survey(G(User), self.group)
        survey_data = {"title": "A way better title"}

        response = self.client.patch(
            self.get_detail_url(survey), survey_data, **self.headers
        )
        survey.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.user, survey.owner)

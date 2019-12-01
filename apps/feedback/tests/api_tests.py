import logging

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status

from apps.feedback.models import (
    Choice,
    Feedback,
    FeedbackRelation,
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

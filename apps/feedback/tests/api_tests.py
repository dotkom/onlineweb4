import logging

from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status

from apps.feedback.models import (
    Choice,
    Feedback,
    MultipleChoiceAnswer,
    MultipleChoiceQuestion,
    MultipleChoiceRelation,
    RatingQuestion,
    Session,
    TextQuestion,
)
from apps.online_oidc_provider.test import OIDCTestCase

from .base_tests import FeedbackTestCaseMixin

logger = logging.getLogger(__name__)


class FeedbackAPITestCase(FeedbackTestCaseMixin, OIDCTestCase):
    url_basename = None

    def get_list_url(self):
        return reverse(f"{self.url_basename}-list")

    def get_detail_url(self, obj):
        return reverse(f"{self.url_basename}-detail", args=[obj.id])

    def create_session(self, feedback_relation=None):
        if not feedback_relation:
            feedback_relation = self.create_feedback_relation(user=self.user)
        session: Session = G(
            Session, user=self.user, feedback_relation=feedback_relation
        )
        return session


class SessionTest(FeedbackAPITestCase):
    url_basename = "feedback_sessions"

    def test_url_returns_403_without_login(self):
        response = self.client.get(self.get_list_url(), **self.bare_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_url_returns_ok_with_login(self):
        response = self.client.get(self.get_list_url(), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_retrieve_a_session(self):
        session = self.create_session()
        response = self.client.get(self.get_detail_url(session), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_create_sessions(self):
        feedback_relation = self.create_feedback_relation(user=self.user)
        response = self.client.post(
            self.get_list_url(),
            {"feedback_relation": feedback_relation.id},
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_create_sessions_when_they_cannot_answer_the_relation(self):
        feedback_relation = self.create_feedback_relation()
        response = self.client.post(
            self.get_list_url(),
            {"feedback_relation": feedback_relation.id},
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_delete_sessions(self):
        session = self.create_session()
        response = self.client.delete(self.get_detail_url(session), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class FeedbackRelationTest(FeedbackAPITestCase):
    url_basename = "feedback_relations"

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


class FeedbackAnswerAPITestCase(FeedbackAPITestCase):
    def setUp(self):
        super().setUp()
        self.feedback: Feedback = G(Feedback)
        self.feedback_relation = self.create_feedback_relation(
            user=self.user, feedback=self.feedback
        )
        self.session = self.create_session(feedback_relation=self.feedback_relation)


class TextAnswerTest(FeedbackAnswerAPITestCase):
    url_basename = "feedback_answer_text"

    def setUp(self):
        super().setUp()

        self.text_question_1: TextQuestion = G(TextQuestion, feedback=self.feedback)
        self.text_question_2: TextQuestion = G(TextQuestion, feedback=self.feedback)

    def test_user_can_answer_text_questions(self):
        answer_data = {
            "question": self.text_question_1.id,
            "session": self.session.id,
            "feedback_relation": self.feedback_relation.id,
            "answer": "An answer to a question",
        }
        response = self.client.post(self.get_list_url(), answer_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_answer_text_questions_with_blank(self):
        answer_data = {
            "question": self.text_question_1.id,
            "session": self.session.id,
            "feedback_relation": self.feedback_relation.id,
            "answer": "",
        }
        response = self.client.post(self.get_list_url(), answer_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("answer"), ["Dette feltet må ikke være blankt."]
        )


class RatingAnswerTest(FeedbackAnswerAPITestCase):
    url_basename = "feedback_answer_rating"

    def setUp(self):
        super().setUp()

        self.rating_question_1: RatingQuestion = G(
            RatingQuestion, feedback=self.feedback
        )
        self.rating_question_2: RatingQuestion = G(
            RatingQuestion, feedback=self.feedback
        )

    def test_user_can_answer_rating_questions(self):
        answer_data = {
            "question": self.rating_question_1.id,
            "session": self.session.id,
            "feedback_relation": self.feedback_relation.id,
            "answer": 1,
        }
        response = self.client.post(self.get_list_url(), answer_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_answer_rating_questions_with_an_invalid_choice(self):
        wrong_answer = -1
        answer_data = {
            "question": self.rating_question_1.id,
            "session": self.session.id,
            "feedback_relation": self.feedback_relation.id,
            "answer": wrong_answer,
        }
        response = self.client.post(self.get_list_url(), answer_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("answer"), [f'"{wrong_answer}" er ikke et gyldig valg.']
        )


class MultipleChoiceAnswerTest(FeedbackAnswerAPITestCase):
    url_basename = "feedback_answer_multiple_choice"

    def setUp(self):
        super().setUp()

        self.question: MultipleChoiceQuestion = G(MultipleChoiceQuestion)
        self.choice_1: Choice = G(Choice, question=self.question)
        self.choice_2: Choice = G(Choice, question=self.question)
        self.choice_3: Choice = G(Choice, question=self.question)
        self.multiple_choice_relation: MultipleChoiceRelation = G(
            MultipleChoiceRelation,
            multiple_choice_relation=self.question,
            feedback=self.feedback,
        )

    def get_answer_data(self, overwrite_data={}):
        answer_data = {
            "question": self.multiple_choice_relation.id,
            "session": self.session.id,
            "feedback_relation": self.feedback_relation.id,
            "answer": self.choice_1.choice,
        }
        answer_data.update(overwrite_data)
        return answer_data

    def test_user_can_answer_multiple_choice_questions(self):
        answer_data = self.get_answer_data()
        response = self.client.post(self.get_list_url(), answer_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.get_list_url(), answer_data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_answer_multiple_choice_questions_only_once(self):
        MultipleChoiceAnswer.objects.create(
            question=self.multiple_choice_relation,
            session=self.session,
            feedback_relation=self.feedback_relation,
            answer=self.choice_1.choice,
        )
        answer_data = self.get_answer_data()

        response = self.client.post(self.get_list_url(), answer_data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_answer_with_unsupported_answer(self):
        answer_data = self.get_answer_data({"answer": "---some-invalid-string---"})
        response = self.client.post(self.get_list_url(), answer_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "ikke et gyldig valg for spørsmålet.",
            response.json().get("non_field_errors")[0],
        )

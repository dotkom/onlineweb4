import logging

from rest_framework import serializers

from .models import (
    Choice,
    Feedback,
    FeedbackRelation,
    FieldOfStudyAnswer,
    GenericSurvey,
    MultipleChoiceAnswer,
    MultipleChoiceQuestion,
    MultipleChoiceRelation,
    RatingAnswer,
    RatingQuestion,
    TextAnswer,
    TextQuestion,
)

logger = logging.getLogger(__name__)


class GenericSurveySerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def update(self, instance: GenericSurvey, validated_data):
        """
        Make sure the original owner is referenced even when another user changes the object.
        """
        validated_data.update({"owner": instance.owner})
        return super().update(instance, validated_data)

    class Meta:
        model = GenericSurvey
        fields = (
            "id",
            "feedback",
            "deadline",
            "allowed_users",
            "created_date",
            "owner",
            "owner_group",
            "title",
        )


class TextQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextQuestion
        fields = ("id", "feedback", "order", "label", "display")


class TextAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextAnswer
        fields = ("id", "question", "answer", "order")


class RatingQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingQuestion
        fields = ("id", "feedback", "order", "label", "display")


class RatingAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingAnswer
        fields = ("id", "answer", "question", "order")


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("id", "choice", "question")


class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = MultipleChoiceQuestion
        fields = ("id", "label", "choices")


class MultipleChoiceRelationManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceRelation
        fields = ("id", "order", "display", "question", "feedback")


class MultipleChoiceRelationSerializer(serializers.ModelSerializer):
    question = MultipleChoiceQuestionSerializer()

    class Meta:
        model = MultipleChoiceRelation
        fields = ("id", "order", "display", "question")


class MultipleChoiceAnswerSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        question_relation: MultipleChoiceRelation = attrs.get("question")
        answer: str = attrs.get("answer")

        allowed_answers = [
            choice.choice for choice in question_relation.question.choices.all()
        ]
        if answer not in allowed_answers:
            raise serializers.ValidationError(
                f"Svaret '{answer}' er ikke et gyldig valg for spørsmålet. "
                f"Gyldige valg er: {allowed_answers}"
            )

        return super().validate(attrs)

    class Meta:
        model = MultipleChoiceAnswer
        fields = ("id", "answer", "question", "order")


class FeedbackAdminSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="feedback_id", read_only=True, required=False)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Feedback
        fields = (
            "id",
            "author",
            "description",
            "display_field_of_study",
            "display_info",
            "available",
            "text_questions",
            "rating_questions",
            "multiple_choice_questions",
        )


class FeedbackReadAllSerializer(serializers.ModelSerializer):
    text_questions = TextQuestionSerializer(many=True)
    rating_questions = RatingQuestionSerializer(many=True)
    multiple_choice_questions = MultipleChoiceRelationSerializer(many=True)
    id = serializers.IntegerField(source="feedback_id")

    class Meta:
        model = Feedback
        fields = (
            "id",
            "author",
            "description",
            "display_field_of_study",
            "display_info",
            "available",
            "text_questions",
            "rating_questions",
            "multiple_choice_questions",
        )
        read_only = True


class FeedbackRelationReadSerializer(serializers.ModelSerializer):
    answered = serializers.SerializerMethodField()
    feedback = FeedbackReadAllSerializer()

    def get_answered(self, obj: FeedbackRelation):
        request = self.context.get("request")
        return obj.answered.filter(pk=request.user.id).exists()

    class Meta:
        model = FeedbackRelation
        fields = (
            "id",
            "gives_mark",
            "deadline",
            "active",
            "created_date",
            "first_mail_sent",
            "answered",
            "description",
            "content_title",
            "feedback",
        )
        read_only = True


class FeedbackRelationListSerializer(serializers.ModelSerializer):
    answered = serializers.SerializerMethodField()

    def get_answered(self, obj: FeedbackRelation):
        request = self.context.get("request")
        return obj.answered.filter(pk=request.user.id).exists()

    class Meta:
        model = FeedbackRelation
        fields = (
            "id",
            "gives_mark",
            "deadline",
            "active",
            "created_date",
            "first_mail_sent",
            "answered",
            "description",
            "content_title",
            "feedback",
        )
        read_only = True


class FeedbackRelationSubmitSerializer(serializers.ModelSerializer):
    text_answers = TextAnswerSerializer(many=True, default=[])
    rating_answers = RatingAnswerSerializer(many=True, default=[])
    multiple_choice_answers = MultipleChoiceAnswerSerializer(many=True, default=[])

    @staticmethod
    def _check_answer_ids(answers: [dict], question_queryset: list) -> bool:
        """
        Check if the submitted answer contains an answer for all questions.
        :param answers: list containing the data for all submitted answers of a type.
        :param question_queryset: the questions of a type which should be answered for this feedback.
        """
        question_ids = sorted([question.id for question in question_queryset])
        answer_question_ids = sorted([answer.get("question").id for answer in answers])
        return answer_question_ids == question_ids

    def validate_text_answers(self, answers: [dict]):
        relation: FeedbackRelation = self.instance
        if not self._check_answer_ids(answers, relation.feedback.text_questions.all()):
            raise serializers.ValidationError(
                "Du har svart på enten for mange eller for få tekstspørsmål"
            )

        return answers

    def validate_rating_answers(self, answers: [dict]):
        relation: FeedbackRelation = self.instance
        if not self._check_answer_ids(
            answers, relation.feedback.rating_questions.all()
        ):
            raise serializers.ValidationError(
                "Du har svart på enten for mange eller for få vurderingssørsmål"
            )

        return answers

    def validate_multiple_choice_answers(self, answers: [dict]):
        relation: FeedbackRelation = self.instance
        if not self._check_answer_ids(
            answers, relation.feedback.multiple_choice_questions.all()
        ):
            raise serializers.ValidationError(
                "Du har svart på enten for mange eller for få flervalgsspørsmål"
            )

        return answers

    def validate(self, data):
        """
        A user should only be allowed to answer if they have are allowed to, and have not previously
        answered the schema.
        """
        request = self.context.get("request")
        relation: FeedbackRelation = self.instance

        if not relation.can_answer(request.user):
            raise serializers.ValidationError(
                "Du har ikke tilgang til å svare på denne undersøkelsen"
            )

        has_answered = relation.answered.filter(pk=request.user.id).exists()
        if has_answered:
            raise serializers.ValidationError(
                "Du har allerede svart på denne undersøkelsen"
            )

        return super().validate(data)

    def update(self, instance: FeedbackRelation, validated_data):
        """
        Submitting an answer for a feedback schema does not allow updating the feedback-relation itself.
        It does only allow updating of the related answers.
        The instance is only manipulated to add the answering user to the set of answered users.
        """
        request = self.context.get("request")

        for answer in validated_data.get("text_answers", []):
            TextAnswer.objects.create(feedback_relation=instance, **answer)

        for answer in validated_data.get("rating_answers", []):
            RatingAnswer.objects.create(feedback_relation=instance, **answer)

        for answer in validated_data.get("multiple_choice_answers", []):
            MultipleChoiceAnswer.objects.create(feedback_relation=instance, **answer)

        FieldOfStudyAnswer.objects.create(
            feedback_relation=instance, answer=request.user.field_of_study
        )

        instance.answered.add(request.user)
        return instance

    class Meta:
        model = FeedbackRelation
        fields = (
            "id",
            "answered",
            "text_answers",
            "rating_answers",
            "multiple_choice_answers",
        )

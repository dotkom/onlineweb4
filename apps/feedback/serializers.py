import logging

from rest_framework import serializers

from .models import (
    Choice,
    Feedback,
    FeedbackRelation,
    MultipleChoiceAnswer,
    MultipleChoiceQuestion,
    MultipleChoiceRelation,
    RatingAnswer,
    RatingQuestion,
    Session,
    TextAnswer,
    TextQuestion,
)

logger = logging.getLogger(__name__)


class AnswerCreateMixin(serializers.Serializer):
    session = serializers.PrimaryKeyRelatedField(queryset=Session.objects.all())
    feedback_relation = serializers.PrimaryKeyRelatedField(
        queryset=FeedbackRelation.objects.all()
    )

    def validate_session(self, session: Session):
        request = self.context.get("request")
        if not request.user == session.user:
            raise serializers.ValidationError(
                "Du kan ikke svare på tilbakemeldingsskjemaer for andre."
            )

        return session

    def validate_feedback_relation(self, feedback_relation: FeedbackRelation):
        request = self.context.get("request")
        if not feedback_relation.can_answer(request.user):
            raise serializers.ValidationError(
                "Du har ikke rettighetene til å svare på dette tilbakemeldingsskjemaet"
            )

        return feedback_relation

    def validate(self, attrs):
        session: Session = attrs.get("session")
        feedback_relation: FeedbackRelation = attrs.get("feedback_relation")
        if session.feedback_relation != feedback_relation:
            raise serializers.ValidationError("Session må tilhøre riktig feedback")

        return super().validate(attrs)


class SessionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ("id", "user", "feedback_relation", "created_date")
        read_only = True


class SessionCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    feedback_relation = serializers.PrimaryKeyRelatedField(
        queryset=FeedbackRelation.objects.all()
    )

    def validate_feedback_relation(self, feedback_relation: FeedbackRelation):
        request = self.context.get("request")
        if not feedback_relation.can_answer(request.user):
            raise serializers.ValidationError(
                "Du har ikke rettighetene til å svare på dette tilbakemeldingsskjemaet"
            )

        return feedback_relation

    class Meta:
        model = Session
        fields = ("id", "user", "feedback_relation", "created_date")


class TextQuestionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextQuestion
        fields = ("id", "feedback", "order", "label", "display")
        read_only = True


class TextAnswerReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextAnswer
        fields = ("id", "question", "feedback_relation", "answer", "order", "session")
        read_only = True


class TextAnswerCreateSerializer(serializers.ModelSerializer, AnswerCreateMixin):
    class Meta:
        model = TextAnswer
        fields = ("id", "question", "feedback_relation", "answer", "order", "session")


class RatingQuestionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingQuestion
        fields = ("id", "feedback", "order", "label", "display")
        read_only = True


class RatingAnswerReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingAnswer
        fields = ("id", "feedback_relation", "answer", "question", "order", "session")
        read_only = True


class RatingAnswerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingAnswer
        fields = ("id", "feedback_relation", "answer", "question", "order", "session")
        read_only = True


class ChoiceReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("id", "choice", "question")


class MultipleChoiceQuestionReadSerializer(serializers.ModelSerializer):
    choices = ChoiceReadSerializer(many=True)

    class Meta:
        model = MultipleChoiceQuestion
        fields = ("id", "label", "choices")


class MultipleChoiceRelationReadSerializer(serializers.ModelSerializer):
    question = MultipleChoiceQuestionReadSerializer(source="multiple_choice_relation")

    class Meta:
        model = MultipleChoiceRelation
        fields = ("id", "order", "display", "question")


class MultipleChoiceAnswerReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceAnswer
        fields = ("id", "feedback_relation", "answer", "question", "order", "session")
        read_only = True


class MultipleChoiceAnswerCreateSerializer(
    serializers.ModelSerializer, AnswerCreateMixin
):
    def validate(self, attrs):
        question: MultipleChoiceRelation = attrs.get("question")
        answer: str = attrs.get("answer")

        allowed_answers = [
            choice.choice for choice in question.multiple_choice_relation.choices.all()
        ]
        if answer not in allowed_answers:
            raise serializers.ValidationError(
                f"Svaret '{answer}' er ikke et gyldig valg for spørsmålet. "
                f"Gyldige valg er: {allowed_answers}"
            )

        return super().validate(attrs)

    class Meta:
        model = MultipleChoiceAnswer
        fields = ("id", "feedback_relation", "answer", "question", "order", "session")


class FeedbackReadSerializer(serializers.ModelSerializer):
    text_questions = TextQuestionReadSerializer(many=True)
    rating_questions = RatingQuestionReadSerializer(many=True)
    multiple_choice_questions = MultipleChoiceRelationReadSerializer(many=True)
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
    feedback = FeedbackReadSerializer()

    def get_answered(self, obj: FeedbackRelation):
        request = self.context.get("request")
        return obj.answered.filter(pk=request.user.id).exists()

    class Meta:
        model = FeedbackRelation
        fields = (
            "id",
            "gives_mark",
            "deadline",
            "feedback",
            "active",
            "created_date",
            "first_mail_sent",
            "answered",
        )
        read_only = True

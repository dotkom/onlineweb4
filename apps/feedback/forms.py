# -*- coding: utf-8 -*-
from django import forms
from apps.feedback.models import RatingAnswer
from apps.feedback.models import RATING_CHOICES
from apps.feedback.models import FieldOfStudyAnswer
from apps.feedback.models import FIELD_OF_STUDY_CHOICES as FOSC
from apps.feedback.models import TextAnswer


class RatingAnswerForm(forms.ModelForm):
    answer = forms.ChoiceField(widget=forms.RadioSelect,
                               choices=RATING_CHOICES)

    def __init__(self, *a, **k):
        super(RatingAnswerForm, self).__init__(*a, **k)
        self.fields['answer'].label = self.instance.question.label

    class Meta:
        model = RatingAnswer
        exclude = ("feedback_relation", "question",)


class FieldOfStudyAnswerForm(forms.ModelForm):
    def __init__(self, *a, **k):
        super(FieldOfStudyAnswerForm, self).__init__(*a, **k)
        self.fields['answer'].label = self.instance.question.label

    def clean_answer(self):
        data = self.cleaned_data['answer']
        if data == -1:
            raise forms.ValidationError('Feltet er påkrevet.')
        return data

    class Meta:
        model = FieldOfStudyAnswer
        exclude = ("feedback_relation", "question",)


class TextAnswerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TextAnswerForm, self).__init__(*args, **kwargs)
        self.fields['answer'].label = self.instance.question.label

    class Meta:
        model = TextAnswer
        exclude = ("feedback_relation", "question",)


def create_answer_forms(fbr, post_data=None):
    """
    Prefix magic to identify forms from post_data.
    """
    answers = []
    for i, question in enumerate(fbr.questions):
        answers.append(answer_form_factory(question, fbr, str(i), post_data))
    return answers


def answer_form_factory(question, feedback_relation, prefix, post_data=None):
    data = {"question": question, "feedback_relation": feedback_relation}
    instance = question.answer.model(**data)
    if question.answer.model == FieldOfStudyAnswer:
        return FieldOfStudyAnswerForm(post_data, instance=instance,
                                      prefix=prefix)

    elif question.answer.model == RatingAnswer:
        return RatingAnswerForm(post_data, instance=instance, prefix=prefix)

    elif question.answer.model == TextAnswer:
        return TextAnswerForm(post_data, instance=instance, prefix=prefix)

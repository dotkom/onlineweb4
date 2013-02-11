# -*- coding: utf-8 -*-
from django import forms
from apps.feedback.models import RatingAnswer
from apps.feedback.models import RATING_CHOICES
from apps.feedback.models import FieldOfStudyAnswer
from apps.feedback.models import TextAnswer
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper


class AnswerForm(forms.ModelForm):
    """
    A superclass for answer forms.
    """
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.html5_required = False
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.fields['answer'].label = self.instance.question.label


class RatingAnswerForm(AnswerForm):
    answer = forms.ChoiceField(widget=forms.RadioSelect,
                               choices=RATING_CHOICES)

    class Meta:
        model = RatingAnswer
        exclude = ("feedback_relation", "question",)


class FieldOfStudyAnswerForm(AnswerForm):

    def clean_answer(self):
        data = self.cleaned_data['answer']
        if data == -1:
            # raise the django field required error
            raise forms.ValidationError(_(u'This field is required.'))
        return data

    class Meta:
        model = FieldOfStudyAnswer
        exclude = ("feedback_relation", "question",)


class TextAnswerForm(AnswerForm):
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

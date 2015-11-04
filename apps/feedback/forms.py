# -*- coding: utf-8 -*-
from django import forms
from apps.feedback.models import RatingAnswer
from apps.feedback.models import MultipleChoiceAnswer
from apps.feedback.models import Choice
from apps.feedback.models import RATING_CHOICES
from apps.feedback.models import FieldOfStudyAnswer
from apps.feedback.models import TextAnswer
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
    answer = forms.ChoiceField(widget=forms.Select(attrs={"class": "rating", "name": "rating"}),
                               choices=RATING_CHOICES)

    class Meta(object):
        model = RatingAnswer
        exclude = ("feedback_relation", "question",)


class FieldOfStudyAnswerForm(AnswerForm):

    def clean_answer(self):
        data = self.cleaned_data['answer']
        return data

    class Meta(object):
        model = FieldOfStudyAnswer
        exclude = ("feedback_relation", "question",)


class TextAnswerForm(AnswerForm):
    answer = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'type': 'text', "rows": "3"}))

    class Meta(object):
        model = TextAnswer
        exclude = ("feedback_relation", "question",)


class MultipleChoiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.html5_required = False
        super(MultipleChoiceForm, self).__init__(*args, **kwargs)

        self.fields['answer'] = forms.ModelChoiceField(
            queryset=Choice.objects.filter(question=self.instance.question.multiple_choice_relation),
            widget=forms.Select(attrs={'class': 'form-control'}))
        self.fields['answer'].label = self.instance.question.multiple_choice_relation.label

    class Meta(object):
        model = MultipleChoiceAnswer
        exclude = ("feedback_relation", "question", "choice")


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

    elif question.answer.model == MultipleChoiceAnswer:
        return MultipleChoiceForm(post_data, instance=instance, prefix=prefix)

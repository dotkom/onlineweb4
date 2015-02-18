# -*- encoding: utf-8 -*-
from django import forms

from apps.article.models import Tag


class TagForm(forms.ModelForm):
    
    class Meta:
        model = Tag


class ArticleForm(forms.ModelForm):
    
    class Meta:
        model = Article
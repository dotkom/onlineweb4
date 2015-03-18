# -*- encoding: utf-8 -*-
from django import forms

from apps.article.models import Tag, Article


class TagForm(forms.ModelForm):
    fields = ['name', 'slug',]
    class Meta:
        model = Tag


class ArticleForm(forms.ModelForm):
    
    class Meta:
        model = Article
        exclude = []
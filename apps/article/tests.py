import datetime
import logging

import pytz
from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.test import APITestCase

from apps.article.models import Article


class ArticleTests(TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.article = G(Article, heading="test_heading")

    def test_article_unicode_is_correct(self):
        self.logger.debug("Article __str__() should return correct heading")
        self.assertEqual(self.article.__str__(), "test_heading")


class ArticleAPIURLTestCase(APITestCase):
    def test_article_list_empty(self):
        url = reverse("article-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_list_exists(self):
        url = reverse("article-list")

        G(Article)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_detail(self):
        in_the_past = datetime.datetime(2000, 1, 1, 0, 0, 0, 0, pytz.UTC)

        article = G(Article, created_date=in_the_past, published_date=in_the_past)

        url = reverse("article-detail", args=(article.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

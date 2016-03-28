import datetime
import logging

from django.core.urlresolvers import reverse
from django.test import TestCase
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.test import APITestCase

from apps.article.models import Article


class ArticleTests(TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.article = G(Article, heading="test_heading")

    def testArticleUnicodeIsCorrect(self):
        self.logger.debug("Article __str__() should return correct heading")
        self.assertEqual(self.article.__str__(), "test_heading")


class ArticleURLTestCase(TestCase):
    def test_article_archive_empty(self):
        url = reverse('article_archive')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_archive_exists(self):
        G(Article)

        url = reverse('article_archive')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_detail(self):
        article = G(Article)

        url = reverse('article_details', args=(article.id, article.slug))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_article_tag(self):
        url = reverse('view_article_tag', args=('slug',))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_archive_year_empty(self):
        url = reverse('article_archive_year', args=(2013,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_archive_year_exists(self):
        created_date = datetime.datetime(2013, 1, 1)
        G(Article, created_date=created_date, published_date=created_date)

        url = reverse('article_archive_year', args=(2013,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_archive_month_empty(self):
        url = reverse('article_archive_month', args=(2013, 'Januar'))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_archive_month_exists(self):
        created_date = datetime.datetime(2013, 1, 1)
        G(Article, created_date=created_date, published_date=created_date)

        url = reverse('article_archive_month', args=(2013, 'Januar'))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ArticleAPIURLTestCase(APITestCase):
    def test_article_list_empty(self):
        url = reverse('article-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_list_exists(self):
        url = reverse('article-list')

        G(Article)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_detail(self):
        in_the_past = datetime.datetime(2000, 1, 1, 0, 0, 0)

        article = G(Article, created_date=in_the_past, published_date=in_the_past)

        url = reverse('article-detail', args=(article.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

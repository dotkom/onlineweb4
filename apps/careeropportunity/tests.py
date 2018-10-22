from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from rest_framework import status

from .models import CareerOpportunity


class CareerOpportunityURLTestCase(TestCase):
    def test_careeropportunity_index(self):
        url = reverse('careeropportunity_index')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_careeropportunity_detail(self):
        past = datetime(2000, 1, 1)
        future = timezone.now() + timedelta(days=1)
        careeropportunity = G(CareerOpportunity, start=past, end=future)

        url = reverse('careeropportunity_details', args=(careeropportunity.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

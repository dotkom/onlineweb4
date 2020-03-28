# -*- coding: utf-8 -*-

import logging

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from guardian.shortcuts import assign_perm
from rest_framework import status

from apps.approval.models import (
    CommitteeApplication,
    CommitteeApplicationPeriod,
    MembershipApproval,
)
from apps.approval.tasks import send_approval_status_update
from apps.authentication.models import Email, OnlineGroup
from apps.authentication.models import OnlineUser as User
from apps.online_oidc_provider.test import OIDCTestCase


class ApprovalTest(TestCase):
    def setUp(self):
        self.applicant = G(
            User, username="sokeren", first_name="Søker", last_name="Søkersen"
        )
        self.approval = G(MembershipApproval, applicant=self.applicant)
        self.approval.new_expiry_date = None
        self.approval.field_of_study = 0
        self.approval.started_date = None
        self.logger = logging.getLogger(__name__)

    def testUnicodeMethod(self):
        self.logger.debug("Testing unicode output for approval")
        self.assertEqual(self.approval.__str__(), "Tom søknad for Søker Søkersen")

        self.approval.new_expiry_date = timezone.now().date()
        self.assertEqual(
            self.approval.__str__(), "Medlemskapssøknad for Søker Søkersen"
        )

        self.approval.field_of_study = 1
        self.approval.started_date = timezone.now().date()
        self.assertEqual(
            self.approval.__str__(),
            "Medlemskaps- og studieretningssøknad for Søker Søkersen",
        )

        self.approval.new_expiry_date = None
        self.assertEqual(
            self.approval.__str__(), "studieretningssøknad for Søker Søkersen"
        )

    def testIsMembershipApplication(self):
        self.logger.debug("Testing method to see if application is for membership")
        self.approval.field_of_study = 1
        self.assertEqual(self.approval.is_membership_application(), False)
        self.approval.started_date = timezone.now().date()
        self.assertEqual(self.approval.is_membership_application(), False)
        self.approval.new_expiry_date = timezone.now().date()
        self.assertEqual(self.approval.is_membership_application(), True)
        self.approval.field_of_study = 0
        self.assertEqual(self.approval.is_membership_application(), True)
        self.approval.started_date = None
        self.assertEqual(self.approval.is_membership_application(), True)
        self.approval.new_expiry_date = None
        self.assertEqual(self.approval.is_membership_application(), False)

    def testIsFOSApplication(self):
        self.logger.debug(
            "Testing method to see if application is for field of study update"
        )
        self.approval.field_of_study = 1
        self.assertEqual(self.approval.is_fos_application(), False)
        self.approval.started_date = timezone.now().date()
        self.assertEqual(self.approval.is_fos_application(), True)
        self.approval.new_expiry_date = timezone.now().date()
        self.assertEqual(self.approval.is_fos_application(), True)
        self.approval.field_of_study = 0
        self.assertEqual(self.approval.is_fos_application(), False)
        self.approval.started_date = None
        self.assertEqual(self.approval.is_fos_application(), False)
        self.approval.new_expiry_date = None
        self.assertEqual(self.approval.is_fos_application(), False)


class EmailTest(TestCase):
    # Create an approval
    def setUp(self):
        self.applicant = G(
            User, username="sokeren", first_name="Søker", last_name="Søkersen"
        )
        G(Email, user=self.applicant, email="test@example.com")
        self.approval = G(MembershipApproval, applicant=self.applicant)
        self.logger = logging.getLogger(__name__)

    def testEmailWhenMembershipDenied(self):
        mail.outbox = []

        self.logger.debug(
            "Testing method to send email when membershipapplications is denied"
        )
        self.approval.approved = False
        self.approval.subject = "Ditt medlemskap i Online er vurdert"
        self.approval.message = "Ditt medlemskap i Online er ikke godkjent. Ta kontakt med Online for begrunnelse."
        send_approval_status_update(self.approval)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)
        # Verify that the subject of the first message is correct.
        self.assertEqual(
            mail.outbox[0].subject, "Soknad om medlemskap i Online er vurdert"
        )
        self.assertIn(
            "Ditt medlemskap i Online er ikke godkjent. Ta kontakt med Online for begrunnelse.",
            str(mail.outbox[0].message()),
        )

    def testEmailWhenMembershipAccepted(self):
        mail.outbox = []

        self.logger.debug(
            "Testing method to send email when membershipapplications is accepted"
        )
        self.approval.approved = True
        self.approval.subject = "Ditt medlemskap i Online er vurdert"
        self.approval.message = "Ditt medlemskap i Online er godkjent."
        send_approval_status_update(self.approval)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)
        # Verify that the subject of the first message is correct.
        self.assertEqual(
            mail.outbox[0].subject, "Soknad om medlemskap i Online er vurdert"
        )
        self.assertIn(
            "Ditt medlemskap i Online er godkjent.", str(mail.outbox[0].message())
        )


class CommitteeApplicationPeriodTestCase(OIDCTestCase):
    def setUp(self):
        self.now = timezone.now()
        self.one_week_ago = self.now - timezone.timedelta(days=7)
        self.two_days_ago = self.now - timezone.timedelta(days=2)
        self.two_days_from_now = self.now + timezone.timedelta(days=2)
        self.one_week_from_now = self.now + timezone.timedelta(days=7)

        assign_perm("approval.add_committeeapplicationperiod", self.user)

        self.committees = [G(OnlineGroup).id, G(OnlineGroup).id]

    def get_list_url(self):
        return reverse("committee-application-periods-list")

    def get_detail_url(self, _id: int):
        return reverse("committee-application-periods-detail", args=[_id])

    def test_anyone_can_get_application_period_list(self):
        response = self.client.get(self.get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anyone_can_get_application_period_detail(self):
        period = G(CommitteeApplicationPeriod)
        response = self.client.get(self.get_detail_url(period.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_application_period(self):
        response = self.client.post(
            self.get_list_url(),
            {
                "title": "Hovedopptak",
                "start": self.now,
                "deadline": self.one_week_from_now,
                "committees": self.committees,
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_application_period_with_deadline_before_start(self):
        response = self.client.post(
            self.get_list_url(),
            {
                "title": "Hovedopptak",
                "start": self.now,
                "deadline": self.two_days_ago,
                "committees": self.committees,
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_application_period_with_deadline_too_close_to_start(self):
        response = self.client.post(
            self.get_list_url(),
            {
                "title": "Hovedopptak",
                "start": self.now,
                "deadline": timezone.now() + timezone.timedelta(hours=23),
                "committees": self.committees,
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_overlapping_application_periods(self):
        CommitteeApplicationPeriod.objects.create(
            title="Hovedopptak",
            start=self.two_days_ago,
            deadline=self.two_days_from_now,
        )

        response = self.client.post(
            self.get_list_url(),
            {
                "title": "Suppleringsopptak",
                "start": self.now,
                "deadline": self.one_week_from_now,
                "committees": self.committees,
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_overlapping_application_periods_inside_another_period(self):
        CommitteeApplicationPeriod.objects.create(
            title="Hovedopptak",
            start=self.one_week_ago,
            deadline=self.one_week_from_now,
        )

        response = self.client.post(
            self.get_list_url(),
            {
                "title": "Suppleringsopptak",
                "start": self.two_days_ago,
                "deadline": self.two_days_from_now,
                "committees": self.committees,
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_overlapping_application_periods(self):
        CommitteeApplicationPeriod.objects.create(
            title="Hovedopptak", start=self.two_days_ago, deadline=self.now
        )

        response = self.client.post(
            self.get_list_url(),
            {
                "title": "Suppleringsopptak",
                "start": self.two_days_from_now,
                "deadline": self.one_week_from_now,
                "committees": self.committees,
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CommitteeApplicationTestCase(OIDCTestCase):
    def setUp(self):
        self.now = timezone.now()
        self.one_week_ago = self.now - timezone.timedelta(days=7)
        self.two_days_ago = self.now - timezone.timedelta(days=2)
        self.two_days_from_now = self.now + timezone.timedelta(days=2)
        self.one_week_from_now = self.now + timezone.timedelta(days=7)

        self.committee1: OnlineGroup = G(OnlineGroup)
        self.committee2: OnlineGroup = G(OnlineGroup)
        self.committee3: OnlineGroup = G(OnlineGroup)

        self.committees_data = [
            {"group": self.committee1.id, "priority": 1},
            {"group": self.committee2.id, "priority": 2},
        ]

        self.application_period: CommitteeApplicationPeriod = G(
            CommitteeApplicationPeriod,
            start=self.one_week_ago,
            deadline=self.two_days_from_now,
        )
        self.application_period.committees.add(self.committee1)
        self.application_period.committees.add(self.committee2)

    def get_list_url(self):
        return reverse("committeeapplications-list")

    def get_detail_url(self, _id: int):
        return reverse("committeeapplications-detail", args=[_id])

    def test_non_authenticated_user_cannot_get_applications(self):
        response = self.client.get(self.get_list_url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_without_perms_cannot_get_applications(self):
        response = self.client.get(self.get_list_url(), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permitted_user_can_get_applications_list(self):
        assign_perm("approval.view_committeeapplication", self.user)
        response = self.client.get(self.get_list_url(), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permitted_user_can_get_applications_detail(self):
        assign_perm("approval.view_committeeapplication", self.user)
        application = G(CommitteeApplication)
        response = self.client.get(self.get_detail_url(application.id), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anyone_can_create_an_application(self):
        response = self.client.post(
            self.get_list_url(),
            {
                "application_text": "--text--",
                "committees": self.committees_data,
                "application_period": self.application_period.id,
                "name": "Test Testesen",
                "email": "test@example.com",
            },
            **self.bare_headers,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_login_application_fails_without_name_and_email(self):
        response = self.client.post(
            self.get_list_url(),
            {
                "application_text": "--text--",
                "application_period": self.application_period.id,
                "committees": self.committees_data,
            },
            **self.bare_headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_login_application_fails_without_name(self):
        response = self.client.post(
            self.get_list_url(),
            {
                "application_text": "--text--",
                "committees": self.committees_data,
                "application_period": self.application_period.id,
                "email": "test@example.com",
            },
            **self.bare_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_login_application_fails_without_email(self):
        response = self.client.post(
            self.get_list_url(),
            {
                "application_text": "--text--",
                "committees": self.committees_data,
                "application_period": self.application_period.id,
                "name": "Test Testesen",
            },
            **self.bare_headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_users_are_assigned_when_creating_an_application(self):
        response = self.client.post(
            self.get_list_url(),
            {
                "application_text": "--text--",
                "committees": self.committees_data,
                "application_period": self.application_period.id,
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get("applicant").get("id"), self.user.id)

    def test_cannot_apply_when_application_period_has_expired(self):
        self.application_period.deadline = self.two_days_ago
        self.application_period.save()

        response = self.client.post(
            self.get_list_url(),
            {
                "application_text": "--text--",
                "committees": self.committees_data,
                "application_period": self.application_period.id,
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_apply_with_committee_not_allowed_in_period(self):
        response = self.client.post(
            self.get_list_url(),
            {
                "application_text": "--text--",
                "committees": [{"group": self.committee3.id, "priority": 1}],
                "application_period": self.application_period.id,
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

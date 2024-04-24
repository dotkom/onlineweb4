import logging

from django.core import mail
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.models import OnlineUser as User
from apps.notifications.constants import PermissionType
from apps.notifications.models import Permission

from .api.serializers import MembershipApprovalSerializer
from .models import MembershipApproval
from .tasks import send_approval_status_update


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


class EmailTest(TransactionTestCase):
    # Create an approval
    def setUp(self):
        self.applicant = G(
            User,
            username="sokeren",
            first_name="Søker",
            last_name="Søkersen",
            email="test@example.com",
        )
        self.approval = G(MembershipApproval, applicant=self.applicant)
        self.logger = logging.getLogger(__name__)

    def testEmailWhenMembershipDenied(self):
        G(Permission, permission_type=PermissionType.APPLICATIONS, force_email=True)
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
            mail.outbox[0].subject, "Søknad om medlemskap i Online er vurdert"
        )
        self.assertIn(
            "Ditt medlemskap i Online er ikke godkjent. Ta kontakt med Online for begrunnelse.",
            str(mail.outbox[0].message()),
        )

    def testEmailWhenMembershipAccepted(self):
        G(Permission, permission_type=PermissionType.APPLICATIONS, force_email=True)
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
            mail.outbox[0].subject, "Søknad om medlemskap i Online er vurdert"
        )
        self.assertIn(
            "Ditt medlemskap i Online er godkjent.", str(mail.outbox[0].message())
        )


class MembershipApprovalTestCase(APITestCase):
    def setUp(self):
        self.user = G(User)
        self.client.force_authenticate(user=self.user)

    def get_list_url(self):
        return reverse("membership-application-list")

    def get_detail_url(self, _id: int):
        return reverse("membership-application-detail", args=[_id])

    def test_non_authenticated_user_cannot_get_applications(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.get_list_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_only_get_own_application(self):
        application = G(MembershipApproval, applicant=self.user)
        not_our_application = G(MembershipApproval)
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json().get("results")
        self.assertEqual(len(results), 1)
        self.assertEqual(results.pop(), MembershipApprovalSerializer(application).data)
        self.assertNotIn(
            MembershipApprovalSerializer(not_our_application).data, results
        )

from django.contrib.auth.models import Group
from django.utils import timezone
from django_dynamic_fixture import G
from rest_framework import status

from apps.companyprofile.models import Company
from apps.events.models import (
    CompanyEvent,
    Extras,
    FieldOfStudyRule,
    GradeRule,
    GroupRestriction,
    RuleBundle,
    UserGroupRule,
)
from apps.events.tests.utils import attend_user_to_event, generate_event, generate_user
from apps.online_oidc_provider.test import OIDCTestCase
from apps.profiles.models import Privacy

from .utils import generate_attendee


class EventsAPITestCase(OIDCTestCase):
    basename = "events_events"

    def setUp(self):
        self.committee = G(Group, name="Bedkom")
        self.user = generate_user(username="_user")
        self.privacy = G(Privacy, user=self.user)
        self.token = self.generate_access_token(self.user)
        self.headers = {**self.headers, **self.generate_headers()}

        self.event = generate_event(organizer=self.committee)
        self.event.attendance_event.registration_start = timezone.now()
        self.event.attendance_event.registration_end = timezone.now() + timezone.timedelta(
            days=2
        )
        self.event.attendance_event.max_capacity = 20
        self.event.attendance_event.save()
        self.attendee1 = generate_attendee(self.event, "test1", "1231")
        self.attendee2 = generate_attendee(self.event, "test2", "4321")
        self.attendees = [self.attendee1, self.attendee2]

    def test_events_list_empty(self):
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_detail(self):

        response = self.client.get(self.get_detail_url(self.event.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_events_list_exists(self):
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        events_list = response.json().get("results")
        event_titles_list = list(map(lambda event: event.get("title"), events_list))

        self.assertIn(self.event.title, event_titles_list)

    def test_filter_companies_in_event_list(self):
        onlinecorp: Company = G(Company, name="onlinecorp")
        bedpres_with_onlinecorp = generate_event(organizer=self.committee)
        G(CompanyEvent, company=onlinecorp, event=bedpres_with_onlinecorp)
        evilcorp: Company = G(Company, name="evilcorp")
        bedpres_with_evilcorp = generate_event(organizer=self.committee)
        G(CompanyEvent, company=evilcorp, event=bedpres_with_evilcorp)

        response = self.client.get(f"{self.get_list_url()}?companies={onlinecorp.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        events_list = response.json().get("results")
        event_titles_list = list(map(lambda event: event.get("id"), events_list))

        self.assertIn(bedpres_with_onlinecorp.id, event_titles_list)
        self.assertNotIn(bedpres_with_evilcorp.id, event_titles_list)

    def test_event_with_group_restriction(self):
        response = self.client.get(self.get_detail_url(self.event.id), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        restricted_to_group: Group = G(Group)
        G(GroupRestriction, event=self.event, groups=[restricted_to_group])

        response = self.client.get(self.get_detail_url(self.event.id), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        attendee = attend_user_to_event(self.event, self.user)

        self.assertIn(attendee, self.event.attendance_event.attendees.all())
        response = self.client.get(self.get_detail_url(self.event.id), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ExtrasTestCase(OIDCTestCase):
    basename = "events_extras"
    model = Extras

    def setUp(self):
        self.committee = G(Group, name="Bedkom")
        self.user.groups.add(self.committee)
        self.object = G(self.model)

    def test_object_list_empty(self):
        response = self.client.get(self.get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_object_detail(self):
        response = self.client.get(self.get_detail_url(self.object.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_object_list_exists(self):
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        object_list = response.json().get("results")
        object_id_list = list(map(lambda obj: obj.get("id"), object_list))

        self.assertIn(self.object.id, object_id_list)


class RuleBundleTestCase(OIDCTestCase):
    basename = "events_rule_bundles"
    model = RuleBundle

    def setUp(self):
        self.committee = G(Group, name="Bedkom")
        self.user.groups.add(self.committee)
        self.object = G(self.model)

    def test_object_list_empty(self):
        response = self.client.get(self.get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_object_detail(self):
        response = self.client.get(self.get_detail_url(self.object.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_object_list_exists(self):
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        object_list = response.json().get("results")
        object_id_list = list(map(lambda obj: obj.get("id"), object_list))

        self.assertIn(self.object.id, object_id_list)


class FieldOfStudyRuleTestCase(OIDCTestCase):
    basename = "events_field_of_study_rules"
    model = FieldOfStudyRule

    def setUp(self):
        self.committee = G(Group, name="Bedkom")
        self.user.groups.add(self.committee)
        self.object = G(self.model)

    def test_object_list_empty(self):
        response = self.client.get(self.get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_object_detail(self):
        response = self.client.get(self.get_detail_url(self.object.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_object_list_exists(self):
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        object_list = response.json().get("results")
        object_id_list = list(map(lambda obj: obj.get("id"), object_list))

        self.assertIn(self.object.id, object_id_list)


class GradeRuleTestCase(OIDCTestCase):
    basename = "events_grade_rules"
    model = GradeRule

    def setUp(self):
        self.committee = G(Group, name="Bedkom")
        self.user.groups.add(self.committee)
        self.object = G(self.model)

    def test_object_list_empty(self):
        response = self.client.get(self.get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_object_detail(self):
        response = self.client.get(self.get_detail_url(self.object.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_object_list_exists(self):
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        object_list = response.json().get("results")
        object_id_list = list(map(lambda obj: obj.get("id"), object_list))

        self.assertIn(self.object.id, object_id_list)


class UserGroupRuleTestCase(OIDCTestCase):
    basename = "events_user_group_rules"
    model = UserGroupRule

    def setUp(self):
        self.committee = G(Group, name="Bedkom")
        self.user.groups.add(self.committee)
        self.object = G(self.model)

    def test_object_list_empty(self):
        response = self.client.get(self.get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_object_detail(self):
        response = self.client.get(self.get_detail_url(self.object.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_object_list_exists(self):
        response = self.client.get(self.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        object_list = response.json().get("results")
        object_id_list = list(map(lambda obj: obj.get("id"), object_list))

        self.assertIn(self.object.id, object_id_list)

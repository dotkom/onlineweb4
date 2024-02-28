from datetime import date, timedelta

from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Position, SpecialPosition
from apps.events.tests.utils import (
    attend_user_to_event,
    generate_company_event,
    generate_event,
    generate_user,
)


class PositionsTestCase(APITestCase):
    def setUp(self):
        self.user: User = generate_user(username="test_user")
        self.other_user: User = generate_user(username="other_user")
        self.client.force_authenticate(user=self.user)

        self.url = reverse("user_positions-list")
        self.id_url = lambda _id: self.url + str(_id) + "/"

        self.period_start = date(2017, 3, 1)
        self.period_end = self.period_start + timedelta(days=366)
        self.position: Position = G(Position, user=self.user)
        self.other_position: Position = G(
            Position,
            user=self.other_user,
            period_start=self.period_start,
            period_end=self.period_end,
        )
        self.position_data = {
            "position": "medlem",
            "period_start": str(self.period_start),
            "period_end": str(self.period_end),
            "committee": "hs",
        }

    def test_positions_view_returns_200(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_view_their_own_positions(self):
        response = self.client.get(self.id_url(self.position.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.position.id)

    def test_user_cannot_view_other_users_positions(self):
        response = self.client.get(self.id_url(self.other_position.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_create_a_position(self):
        response = self.client.post(self.url, self.position_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json().get("position"), self.position_data.get("position")
        )

    def test_user_can_only_create_positions_for_themselves(self):
        response = self.client.post(
            self.url, {**self.position_data, "user": self.other_user.id}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_create_positions_with_start_after_end(self):
        date_before_period_start = self.period_start - timedelta(days=1)

        response = self.client.post(
            self.url,
            {**self.position_data, "period_end": str(date_before_period_start)},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("non_field_errors"),
            ["Vervets starttid kan ikke være etter vervets sluttid"],
        )

    def test_user_cannot_create_positions_with_start_at_same_time_as_end(self):
        response = self.client.post(
            self.url,
            {
                **self.position_data,
                "period_end": str(self.period_start),
                "period_start": str(self.period_start),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("non_field_errors"),
            ["Du kan ikke starte og avslutte et verv på samme dag"],
        )

    def test_user_can_update_a_position(self):
        new_period_end = str(self.period_end + timedelta(days=365))

        response = self.client.patch(
            self.id_url(self.position.id),
            {
                "period_start": str(
                    self.period_start
                ),  # Both are currently required to make a change
                "period_end": new_period_end,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("period_end"), new_period_end)

    def test_user_can_delete_a_position(self):
        response = self.client.delete(self.id_url(self.position.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(self.position, self.user.positions.all())

    def test_user_cannot_delete_other_users_positions(self):
        other_position = self.other_position
        response = self.client.delete(self.id_url(self.other_position.id))
        other_position.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.other_position, other_position)


class SpecialPositionsTestCase(APITestCase):
    def setUp(self):
        self.user: User = generate_user(username="test_user")
        self.other_user: User = generate_user(username="other_user")
        self.client.force_authenticate(user=self.user)

        self.url = reverse("user_special_positions-list")
        self.id_url = lambda _id: self.url + str(_id) + "/"
        self.special_position: SpecialPosition = G(SpecialPosition, user=self.user)
        self.other_special_position: SpecialPosition = G(
            SpecialPosition, user=self.other_user
        )

    def test_special_positions_returns_200(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_view_their_own_special_positions(self):
        response = self.client.get(self.id_url(self.special_position.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.special_position.id)

    def test_user_cannot_view_other_users_special_positions(self):
        response = self.client.get(self.id_url(self.other_special_position.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestDumpData(APITestCase):
    def setUp(self):
        self.user: User = generate_user(username="test_user")
        self.other_user: User = generate_user(username="other_user")
        self.client.force_authenticate(user=self.user)

        self.url = reverse("users-dump-data")

        self.period_start = date(2017, 3, 1)
        self.period_end = self.period_start + timedelta(days=366)
        self.position: Position = G(Position, user=self.user)
        self.position_data = {
            "position": "medlem",
            "period_start": str(self.period_start),
            "period_end": str(self.period_end),
            "committee": "hs",
        }

    def test_dump_data_contains_name(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("name"), self.user.get_full_name())

    def test_dump_data_contains_attendees(self):
        self.event = generate_event()
        self.attendee1 = attend_user_to_event(user=self.user, event=self.event)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get("attendees")), 1)

    def test_dump_data_contains_companies(self):
        self.event = generate_company_event()
        attend_user_to_event(user=self.user, event=self.event)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json().get("attendees")[0].get("companies"),
            [{"name": "onlinecorp"}],
        )

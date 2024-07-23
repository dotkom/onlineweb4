from datetime import date, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import F, G
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.models import OnlineUser as User
from apps.marks.models import (
    DURATION,
    Mark,
    MarkRuleSet,
    RuleAcceptance,
    Suspended,
    Suspension,
    delay_expiry_for_freeze_periods,
    sanction_users,
    user_sanctions,
)


def test_cause_defaults_weight(db):
    rs = G(MarkRuleSet, duration=timedelta(days=14))
    mark = Mark(title="Test2Prikk", cause=Mark.Cause.LATE_ARRIVAL, ruleset=rs)
    mark.save()
    assert mark.weight == 3


@pytest.mark.parametrize(
    "given_date,expected_last_day",
    [
        (date(2024, 2, 1), date(2024, 2, 1) + timedelta(days=DURATION)),
        # summer vacation, on expiry the mark is no longer in effect
        (date(2024, 5, 24), date(2024, 8, 21)),
        (date(2024, 9, 1), date(2024, 9, 1) + timedelta(days=DURATION)),
        # winter vacation
        (
            date(2024, 11, 25),
            date(2024, 11, 25) + timedelta(days=DURATION) + timedelta(days=36),
        ),
        # between winter vacation and new year
        (date(2024, 1, 1), date(2024, 1, 24)),
        (date(2024, 1, 9), date(2024, 1, 24)),
        (date(2024, 1, 10), date(2024, 1, 24)),
        (date(2024, 12, 15), date(2025, 1, 24)),
        (date(2024, 12, 5), date(2025, 1, 24)),
        (date(2024, 1, 11), date(2024, 1, 25)),
        (date(2024, 7, 1), date(2024, 8, 29)),
        (date(2024, 6, 1), date(2024, 8, 29)),
        (date(2024, 8, 14), date(2024, 8, 29)),
        (date(2024, 8, 15), date(2024, 8, 29)),
        (date(2024, 8, 16), date(2024, 8, 30)),
        (date(2022, 2, 2), date(2022, 2, 16)),
    ],
)
def test_freeze_duration(given_date, expected_last_day):
    actual = delay_expiry_for_freeze_periods(
        given_date, given_date + timedelta(days=DURATION)
    )
    assert expected_last_day == actual


def test_suspensions_and_marks_over_time(db):
    user = G(User)
    now = timezone.datetime(
        year=2024, month=9, day=1, hour=9, tzinfo=ZoneInfo("Europe/Oslo")
    )
    m = G(
        Mark,
        n=3,
        weight=3,
        added_date=now.date() - timedelta(days=7),
        ruleset=F(duration=timedelta(days=14)),
    )

    for mark in m:
        sanction_users(mark, [user], now)

    assert type(user_sanctions(user, now.date())) is Suspended

    active_suspensions = Suspension.active_suspensions(user, now.date())
    assert len(active_suspensions) == 1

    s = active_suspensions[0]
    expected_end = now.date() + timedelta(days=14)
    assert s.cause == Suspension.Cause.MARKS
    assert s.expiration_date == expected_end
    assert s.created_time == now


class MarkRuleSetTest(TestCase):
    def setUp(self):
        self.rule_set: MarkRuleSet = G(MarkRuleSet, version="1.0.0")

    def test_creating_new_rule_set_supplants_the_old(self):
        new_rule_set: MarkRuleSet = G(MarkRuleSet)

        self.assertEqual(MarkRuleSet.get_current_rule_set(), new_rule_set)

    def test_creating_new_rule_set_for_the_future_does_not_supplant_yet(self):
        future_date = timezone.now() + timezone.timedelta(days=2)
        G(MarkRuleSet, valid_from_date=future_date)

        self.assertEqual(MarkRuleSet.get_current_rule_set(), self.rule_set)

    def test_creating_a_ruleset_for_the_past_does_not_replace_current(self):
        past_date = timezone.now() - timezone.timedelta(days=2)
        G(MarkRuleSet, valid_from_date=past_date)

        self.assertEqual(MarkRuleSet.get_current_rule_set(), self.rule_set)

    def test_changing_an_old_ruleset_does_not_replace_the_current(self):
        new_rule_set: MarkRuleSet = G(MarkRuleSet)
        self.rule_set.version = "1.0.1"
        self.rule_set.content = "Changed the old rules"
        self.rule_set.save()

        self.assertEqual(MarkRuleSet.get_current_rule_set(), new_rule_set)


class MarkRuleAcceptanceTest(TestCase):
    def setUp(self):
        self.rule_set: MarkRuleSet = G(MarkRuleSet, version="1.0.0")
        self.user: User = G(User)

    def test_accepting_mark_rules_sets_them_as_accepted(self):
        MarkRuleSet.accept_mark_rules(self.user)

        self.assertTrue(self.user.mark_rules_accepted)

    def test_creating_new_mark_rules_sets_accepted_to_false(self):
        MarkRuleSet.accept_mark_rules(self.user)
        self.assertTrue(self.user.mark_rules_accepted)

        G(MarkRuleSet, valid_from_date=timezone.now())
        self.assertFalse(self.user.mark_rules_accepted)


class MarkRuleSetAPITest(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user: User = G(User, username="test_user")
        self.client.force_authenticate(user=self.user)

        self.url = reverse("mark_rule_sets-list")
        self.id_url = lambda _id: reverse("mark_rule_sets-detail", args=[_id])

        self.rule_set: MarkRuleSet = G(MarkRuleSet, version="1.0.0")

    def test_marks_rule_sets_api_returns_ok_without_auth(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_can_view_mark_rules(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.id_url(self.rule_set.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MarkRuleAcceptanceAPITest(APITestCase):
    def setUp(self):
        super().setUp()
        self.user: User = G(User, username="test_user")
        self.client.force_authenticate(user=self.user)

        self.url = reverse("mark_rule_acceptance-list")
        self.id_url = lambda _id: reverse("mark_rule_acceptance-detail", args=[_id])

        self.rule_set: MarkRuleSet = G(MarkRuleSet, version="1.0.0")

    def create_rule_acceptance(self):
        self.rule_acceptance: RuleAcceptance = G(
            RuleAcceptance, user=self.user, rule_set=self.rule_set
        )

    def test_marks_rule_acceptance_api_returns_unauthorized_without_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_marks_rule_acceptance_api_returns_ok_with_auth(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_view_mark_acceptance(self):
        self.create_rule_acceptance()

        response = self.client.get(self.id_url(self.rule_acceptance.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_cannot_view_mark_acceptance_for_other_users(self):
        other_user: User = G(User)
        rule_acceptance: RuleAcceptance = G(
            RuleAcceptance, user=other_user, rule_set=self.rule_set
        )
        response = self.client.get(self.id_url(rule_acceptance.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_accept_mark_rules(self):
        response = self.client.post(self.url, {"rule_set": self.rule_set.id})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_not_accept_mark_rules_for_other_users(self):
        other_user: User = G(User)

        response = self.client.post(
            self.url, {"user": other_user.id, "rule_set": self.rule_set.id}
        )

        rule_acceptance = RuleAcceptance.objects.filter(
            user=other_user, rule_set=self.rule_set
        ).first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(rule_acceptance)

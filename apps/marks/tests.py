import logging
from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from rest_framework import status

from apps.authentication.models import OnlineUser as User
from apps.marks.models import (
    Mark,
    MarkRuleSet,
    MarkUser,
    RuleAcceptance,
    _get_with_duration_and_vacation,
)
from apps.online_oidc_provider.test import OIDCTestCase


class MarksTest(TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.user = G(User)
        self.mark = G(Mark, title="Testprikk", added_date=timezone.now().date())
        self.userentry = G(MarkUser, user=self.user, mark=self.mark)

    # Rewrite to check
    #    def testMarksActive(self):
    #        self.logger.debug("Testing if Mark is active")
    #        self.assertTrue(self.mark.is_active)

    def testMarkUnicode(self):
        self.logger.debug("Testing Mark unicode with dynamic fixtures")
        self.assertEqual(str(self.mark), "Prikk for Testprikk")

    def testMarkUser(self):
        self.logger.debug("Testing MarkUser unicode with dynamic fixtures")
        self.assertEqual(
            str(self.userentry), "Mark entry for user: %s" % self.user.get_full_name()
        )

    def testGettingExpirationDateWithNoVacationInSpring(self):
        self.logger.debug("Testing expiration date with no vacation span in the spring")
        d = date(2013, 2, 1)
        self.assertEqual(date(2013, 3, 3), _get_with_duration_and_vacation(d))

    def testGettingExpirationDateWithSummerVacation(self):
        self.logger.debug("Testing expiration date with the summer vacation span")
        d = date(2013, 5, 15)
        self.assertEqual(date(2013, 8, 28), _get_with_duration_and_vacation(d))

    def testGettingExpirationDateWithNoVacationInFall(self):
        self.logger.debug("Testing expiration date with no vacation span in the spring")
        d = date(2013, 9, 1)
        self.assertEqual(date(2013, 10, 1), _get_with_duration_and_vacation(d))

    def testGettingExpirationDateWithWinterVacation(self):
        self.logger.debug("Testing expiration date with the summer vacation span")
        d = date(2013, 11, 15)
        self.assertEqual(date(2014, 1, 29), _get_with_duration_and_vacation(d))

    def testGettingExpirationDateWhenDateBetweenNewYearsAndEndOfWinterVacation(self):
        self.logger.debug("Testing expiration date with no vacation span in the spring")
        d = date(2013, 1, 1)
        self.assertEqual(date(2013, 2, 14), _get_with_duration_and_vacation(d))

    def testGettingExpirationDateWhenDateBetweenStartOfWinterVacationAndNewYears(self):
        self.logger.debug("Testing expiration date with no vacation span in the spring")
        d = date(2013, 12, 15)
        self.assertEqual(date(2014, 2, 14), _get_with_duration_and_vacation(d))

    def testGettingExpirationDateWhenDateInSummerVacation(self):
        self.logger.debug("Testing expiration date with no vacation span in the spring")
        d = date(2013, 7, 1)
        self.assertEqual(date(2013, 9, 14), _get_with_duration_and_vacation(d))


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


class MarkRuleSetAPITest(OIDCTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user: User = G(User, username="test_user")
        self.token = self.generate_access_token(self.user)
        self.headers = {**self.generate_headers(), **self.bare_headers}

        self.url = reverse("mark_rule_sets-list")
        self.id_url = lambda _id: reverse("mark_rule_sets-detail", args=[_id])

        self.rule_set: MarkRuleSet = G(MarkRuleSet, version="1.0.0")

    def test_marks_rule_sets_api_returns_ok_without_auth(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_can_view_mark_rules(self):
        response = self.client.get(self.id_url(self.rule_set.id), **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MarkRuleAcceptanceAPITest(OIDCTestCase):
    def setUp(self):
        super().setUp()
        self.user: User = G(User, username="test_user")
        self.token = self.generate_access_token(self.user)
        self.headers = {**self.generate_headers(), **self.bare_headers}

        self.url = reverse("mark_rule_acceptance-list")
        self.id_url = lambda _id: reverse("mark_rule_acceptance-detail", args=[_id])

        self.rule_set: MarkRuleSet = G(MarkRuleSet, version="1.0.0")

    def create_rule_acceptance(self):
        self.rule_acceptance: RuleAcceptance = G(
            RuleAcceptance, user=self.user, rule_set=self.rule_set
        )

    def test_marks_rule_acceptance_api_returns_forbidden_without_auth(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_marks_rule_acceptance_api_returns_ok_with_auth(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_view_mark_acceptance(self):
        self.create_rule_acceptance()

        response = self.client.get(self.id_url(self.rule_acceptance.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_cannot_view_mark_acceptance_for_other_users(self):
        other_user: User = G(User)
        rule_acceptance: RuleAcceptance = G(
            RuleAcceptance, user=other_user, rule_set=self.rule_set
        )
        response = self.client.get(self.id_url(rule_acceptance.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_accept_mark_rules(self):
        response = self.client.post(
            self.url, {"rule_set": self.rule_set.id}, **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_not_accept_mark_rules_for_other_users(self):
        other_user: User = G(User)

        response = self.client.post(
            self.url,
            {"user": other_user.id, "rule_set": self.rule_set.id},
            **self.headers
        )

        rule_acceptance = RuleAcceptance.objects.filter(
            user=other_user, rule_set=self.rule_set
        ).first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(rule_acceptance)

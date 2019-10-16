import json

import mock
from django.core import mail
from django.test import TestCase
from django_dynamic_fixture import G

from apps.approval.models import MembershipApproval
from apps.authentication.models import OnlineUser
from apps.dataporten.study.tasks import (
    fetch_groups_information,
    find_user_study_and_update,
    set_ntnu_username,
)

from .course_test_data import (
    INFORMATICS_BACHELOR_STUDY_PROGRAMME,
    INFORMATICS_MASTER_STUDY_PROGRAMME,
    ITGK_ACTIVE,
    PVS_ACTIVE,
    load_course,
)


class StudyRequestsTestCase(TestCase):
    def _mock_request(self, content=list()):
        resp = mock.Mock()
        resp.content = json.dumps(content).encode('UTF-8')

        return resp

    @mock.patch('requests.get')
    def test_fetch_groups_information(self, mocked_request):
        groups = []

        mocked_request.return_value = self._mock_request(content=groups)

        self.assertEqual(groups, fetch_groups_information(''))


class StudyUpdatingTestCase(TestCase):
    def test_find_user_study_and_update_1st_grader(self):
        user = G(OnlineUser)
        groups = [
            INFORMATICS_BACHELOR_STUDY_PROGRAMME,
            load_course(ITGK_ACTIVE, years_ago=0)
        ]

        resp = find_user_study_and_update(user, groups)

        self.assertTrue(resp)
        application = MembershipApproval.objects.get(applicant=user)

        self.assertTrue(application.approved)
        self.assertTrue(application.processed)

        self.assertEqual(len(mail.outbox), 0)

    def test_find_user_study_and_update_5th_grader(self):
        user = G(OnlineUser)
        groups = [
            INFORMATICS_MASTER_STUDY_PROGRAMME,
            load_course(PVS_ACTIVE, active=True)
        ]

        resp = find_user_study_and_update(user, groups)

        self.assertTrue(resp)
        application = MembershipApproval.objects.get(applicant=user)

        self.assertTrue(application.approved)
        self.assertTrue(application.processed)

        self.assertEqual(len(mail.outbox), 0)


class UserUpdatingTestCase(TestCase):
    def test_set_ntnu_username(self):
        user = G(OnlineUser)
        set_ntnu_username(user, "testname")
        self.assertEqual(user.ntnu_username, "testname")

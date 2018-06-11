from unittest import skip

from dateutil.parser import parse
from django.test import TestCase
from freezegun import freeze_time

from apps.authentication.models import FIELD_OF_STUDY_CHOICES
from apps.dataporten.study.courses import GROUP_IDENTIFIERS
from apps.dataporten.study.utils import (get_bachelor_year, get_course_finish_date,
                                         get_field_of_study, get_group_name, get_master_year,
                                         get_study, get_year, get_year_from_course)

from .course_test_data import (INFORMATICS_BACHELOR_STUDY_PROGRAMME,
                               INFORMATICS_MASTER_STUDY_PROGRAMME, ITGK_ACTIVE, ITGK_EXPIRED,
                               NON_INFORMATICS_COURSE_EXPIRED, PROJECT1_ACTIVE, PROJECT1_EXPIRED,
                               PROJECT2_ACTIVE, PVS_ACTIVE, load_course)


class DataProcessingTestCase(TestCase):
    def setUp(self):
        self.groups = [
            NON_INFORMATICS_COURSE_EXPIRED,
        ]

    def test_get_study_empty_if_not_informatics(self):
        self.assertEqual({}, get_study(self.groups))

    def test_get_study_equals_bit(self):
        bit_course = INFORMATICS_BACHELOR_STUDY_PROGRAMME
        groups = [bit_course]

        self.assertEqual(get_group_name(bit_course), get_group_name(get_study(groups)))

    def test_get_study_equals_mit(self):
        mit_course = INFORMATICS_MASTER_STUDY_PROGRAMME
        groups = [mit_course]

        self.assertEqual(get_group_name(mit_course), get_group_name(get_study(groups)))

    @skip('not sure if it is possible to have two studies at once')
    def test_get_study_equals_mit_if_bit_and_mit(self):
        mit_course = INFORMATICS_MASTER_STUDY_PROGRAMME
        groups = [INFORMATICS_BACHELOR_STUDY_PROGRAMME, INFORMATICS_MASTER_STUDY_PROGRAMME]

        self.assertEqual(get_group_name(mit_course), get_group_name(get_study(groups)))

    def test_get_course_finish_date(self):
        course = load_course(ITGK_EXPIRED)
        expiry_date = parse(course.get('membership').get('notAfter'))

        self.assertEqual(expiry_date, get_course_finish_date(course))

    def test_get_course_finish_date_no_date(self):
        course = load_course(ITGK_ACTIVE)
        # Sneaky hacky
        del course['membership']['notAfter']

        self.assertEqual(None, get_course_finish_date(course))

    def test_get_course_finish_date_illegal_date(self):
        course = load_course(ITGK_ACTIVE)
        course['membership']['notAfter'] = 'definitely not a date'

        self.assertEqual(None, get_course_finish_date(course))

    @freeze_time("2010-10-01 12:00")
    def test_get_year_from_course_itgk_1st_grader_fall(self):
        course = load_course(ITGK_EXPIRED, years_ago=0)
        year = get_year_from_course(course, get_course_finish_date(course))

        self.assertEqual(0, year)

    @freeze_time("2011-03-01 12:00")
    def test_get_year_from_course_itgk_1st_grader_spring(self):
        course = load_course(ITGK_EXPIRED, years_ago=1)
        year = get_year_from_course(course, get_course_finish_date(course))

        self.assertEqual(1, year)

    @freeze_time("2010-10-01 12:00")
    def test_get_year_from_course_itgk_2nd_grader_fall(self):
        course = load_course(ITGK_EXPIRED, years_ago=1)
        course_finish_date = get_course_finish_date(course)
        year = get_year_from_course(course, course_finish_date)

        self.assertEqual(1, year)

    @freeze_time("2010-10-01 12:00")
    def test_get_year_from_course_itgk_3rd_grader_fall(self):
        course = load_course(ITGK_EXPIRED, years_ago=2)
        course_finish_date = get_course_finish_date(course)
        year = get_year_from_course(course, course_finish_date)

        self.assertEqual(2, year)

    @freeze_time("2010-10-01 12:00")
    def test_get_year_from_course_project1_2nd_grader_fall(self):
        course = load_course(PROJECT1_ACTIVE, years_ago=0)
        course_finish_date = get_course_finish_date(course)
        year = get_year_from_course(course, course_finish_date)

        self.assertEqual(1, year)

    @freeze_time("2010-10-01 12:00")
    def test_get_bachelor_year_1st_grader(self):
        groups = [load_course(ITGK_ACTIVE, years_ago=0)]

        self.assertEqual(1, get_bachelor_year(groups))

    @freeze_time("2010-10-01 12:00")
    def test_get_bachelor_year_2nd_grader(self):
        groups = [
            load_course(ITGK_EXPIRED, years_ago=1),
            load_course(PROJECT1_ACTIVE, years_ago=0),
        ]

        self.assertEqual(2, get_bachelor_year(groups))

    @freeze_time("2010-10-01 12:00")
    def test_get_bachelor_year_3rd_grader_fall(self):
        groups = [
            load_course(ITGK_EXPIRED, years_ago=2),
            load_course(PROJECT1_EXPIRED, years_ago=1),
        ]

        self.assertEqual(3, get_bachelor_year(groups))

    @freeze_time("2011-03-01 12:00")
    def test_get_bachelor_year_3rd_grader_spring(self):
        groups = [
            load_course(ITGK_EXPIRED, years_ago=2),
            load_course(PROJECT1_EXPIRED, years_ago=1),
            load_course(PROJECT2_ACTIVE, years_ago=0),
        ]

        self.assertEqual(3, get_bachelor_year(groups))

    @freeze_time("2010-10-01 12:00")
    def test_get_master_year_4th_grader_fall(self):
        groups = []

        self.assertEqual(4, get_master_year(groups))

    @freeze_time("2010-10-01 12:00")
    def test_get_master_year_5th_grader_fall(self):
        groups = [
            load_course(PVS_ACTIVE, active=True),
        ]

        self.assertEqual(5, get_master_year(groups))

    @freeze_time("2010-10-01 12:00")
    def test_get_field_of_study_bachelor(self):
        groups = [
            INFORMATICS_BACHELOR_STUDY_PROGRAMME,
        ]

        self.assertEqual(FIELD_OF_STUDY_CHOICES[1][0], get_field_of_study(groups))

    @freeze_time("2010-10-01 12:00")
    def test_get_field_of_study_master_pvs(self):
        groups = [
            PVS_ACTIVE,
        ]

        self.assertEqual(FIELD_OF_STUDY_CHOICES[2][0], get_field_of_study(groups))

    @freeze_time("2010-10-01 12:00")
    def test_get_year_1st_grader_fall(self):
        groups = [
            INFORMATICS_BACHELOR_STUDY_PROGRAMME,
            load_course(ITGK_ACTIVE)
        ]

        self.assertEqual(1, get_year(GROUP_IDENTIFIERS['BACHELOR'], groups))

    @freeze_time("2010-10-01 12:00")
    def test_get_year_2nd_grader_fall(self):
        groups = [
            INFORMATICS_BACHELOR_STUDY_PROGRAMME,
            load_course(ITGK_EXPIRED, years_ago=1)
        ]

        self.assertEqual(2, get_year(GROUP_IDENTIFIERS['BACHELOR'], groups))

    @freeze_time("2010-10-01 12:00")
    def test_get_year_3rd_grader_fall(self):
        groups = [
            INFORMATICS_BACHELOR_STUDY_PROGRAMME,
            load_course(ITGK_EXPIRED, years_ago=2)
        ]

        self.assertEqual(3, get_year(GROUP_IDENTIFIERS['BACHELOR'], groups))

    @freeze_time("2010-10-01 12:00")
    def test_get_year_4th_grader_fall(self):
        groups = [
            INFORMATICS_MASTER_STUDY_PROGRAMME,
        ]

        self.assertEqual(4, get_year(GROUP_IDENTIFIERS['MASTER'], groups))

    @freeze_time("2010-10-01 12:00")
    def test_get_year_5th_grader_fall(self):
        groups = [
            INFORMATICS_MASTER_STUDY_PROGRAMME,
            load_course(PVS_ACTIVE, active=True),
        ]

        self.assertEqual(5, get_year(GROUP_IDENTIFIERS['MASTER'], groups))

    def test_get_year_not_informatics(self):
        self.assertEqual(0, get_year('DEFINITELY_NOT_INFORMATICS', []))

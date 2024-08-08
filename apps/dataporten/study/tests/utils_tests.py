import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from django.test import TestCase
from django.utils.dateparse import parse_datetime

from apps.authentication.constants import FieldOfStudyType
from apps.dataporten.study.courses import GROUP_IDENTIFIERS
from apps.dataporten.study.utils import (
    get_bachelor_year,
    get_course_finish_date,
    get_field_of_study,
    get_group_name,
    get_master_year,
    get_study,
    get_year,
    get_year_from_course,
)

from .course_test_data import (
    INFORMATICS_BACHELOR_STUDY_PROGRAMME,
    INFORMATICS_MASTER_PVS_SPECIALIZATION,
    INFORMATICS_MASTER_STUDY_PROGRAMME,
    ITGK_ACTIVE,
    ITGK_EXPIRED,
    NON_INFORMATICS_COURSE_EXPIRED,
    PROJECT1_ACTIVE,
    PROJECT1_EXPIRED,
    PROJECT2_ACTIVE,
    PROJECT2_EXPIRED,
    PVS_ACTIVE,
    load_course,
)

DIR_NAME = os.path.dirname(os.path.realpath(__file__))

DUMPS = Path(DIR_NAME) / "data"
SPRING = datetime(year=2018, month=4, day=1, hour=12, tzinfo=ZoneInfo("Europe/Oslo"))
FALL = datetime(year=2017, month=10, day=1, hour=12, tzinfo=ZoneInfo("Europe/Oslo"))


class DataProcessingTestCase(TestCase):
    def setUp(self):
        self.groups = [NON_INFORMATICS_COURSE_EXPIRED]

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

    def test_get_course_finish_date(self):
        course = load_course(ITGK_EXPIRED)
        expiry_date = parse_datetime(course.get("membership").get("notAfter"))

        self.assertEqual(expiry_date, get_course_finish_date(course))

    def test_get_course_finish_date_no_date(self):
        course = load_course(ITGK_ACTIVE)
        # Sneaky hacky
        del course["membership"]["notAfter"]

        self.assertEqual(None, get_course_finish_date(course))

    def test_get_course_finish_date_illegal_date(self):
        course = load_course(ITGK_ACTIVE, now=FALL)
        course["membership"]["notAfter"] = "definitely not a date"

        self.assertEqual(None, get_course_finish_date(course))

    def test_get_year_from_course_itgk_1st_grader_fall(self):
        course = load_course(ITGK_EXPIRED, years_ago=0, now=FALL)
        year = get_year_from_course(course, get_course_finish_date(course), FALL)

        self.assertEqual(1, year)

    def test_get_year_from_course_itgk_1st_grader_spring(self):
        course = load_course(ITGK_EXPIRED, years_ago=1, now=SPRING)
        year = get_year_from_course(course, get_course_finish_date(course), SPRING)

        self.assertEqual(1, year)

    def test_get_year_from_course_itgk_2nd_grader_fall(self):
        course = load_course(ITGK_EXPIRED, years_ago=1, now=FALL)
        course_finish_date = get_course_finish_date(course)
        year = get_year_from_course(course, course_finish_date, FALL)

        self.assertEqual(2, year)

    def test_get_year_from_course_itgk_3rd_grader_fall(self):
        course = load_course(ITGK_EXPIRED, years_ago=2, now=FALL)
        course_finish_date = get_course_finish_date(course)
        year = get_year_from_course(course, course_finish_date, FALL)

        self.assertEqual(3, year)

    def test_get_year_from_course_project1_2nd_grader_fall(self):
        course = load_course(PROJECT1_ACTIVE, years_ago=0, now=FALL)
        course_finish_date = get_course_finish_date(course)
        year = get_year_from_course(course, course_finish_date, FALL)

        self.assertEqual(2, year)

    def test_get_field_of_study_bachelor(self):
        groups = [INFORMATICS_BACHELOR_STUDY_PROGRAMME]

        self.assertEqual(FieldOfStudyType.BACHELOR, get_field_of_study(groups))

    def test_get_field_of_study_master_pvs(self):
        groups = [
            load_course(INFORMATICS_MASTER_PVS_SPECIALIZATION, active=True, now=FALL)
        ]

        self.assertEqual(
            FieldOfStudyType.SOFTWARE_ENGINEERING, get_field_of_study(groups)
        )


def test_get_year_no_study():
    assert 0 == get_year("DEFINITELY_NOT_INFORMATICS", [])


@pytest.mark.parametrize(
    "groups,expected_year",
    [
        ([load_course(PVS_ACTIVE, active=True, now=FALL)], 5),
        ([], 4),
    ],
)
def test_get_master_year(groups, expected_year):
    assert expected_year == get_master_year(groups)


@pytest.mark.parametrize(
    "groups,expected_year,application_time",
    [
        (
            [
                INFORMATICS_BACHELOR_STUDY_PROGRAMME,
                load_course(ITGK_EXPIRED, years_ago=2, now=FALL),
            ],
            3,
            FALL,
        ),
        (
            [
                INFORMATICS_BACHELOR_STUDY_PROGRAMME,
                load_course(ITGK_EXPIRED, years_ago=1, now=FALL),
            ],
            2,
            FALL,
        ),
        (
            [
                INFORMATICS_BACHELOR_STUDY_PROGRAMME,
                load_course(ITGK_ACTIVE, now=FALL),
            ],
            1,
            FALL,
        ),
        (
            [
                load_course(ITGK_EXPIRED, years_ago=3, now=FALL),
                load_course(PROJECT1_EXPIRED, years_ago=2, now=FALL),
                load_course(PROJECT2_EXPIRED, years_ago=1, now=FALL),
            ],
            3,
            FALL,
        ),
        (
            [
                load_course(ITGK_EXPIRED, years_ago=2, now=FALL),
                load_course(PROJECT1_EXPIRED, years_ago=1, now=FALL),
                load_course(PROJECT2_ACTIVE, years_ago=0, now=FALL),
            ],
            3,
            SPRING,
        ),
        (
            [
                load_course(ITGK_EXPIRED, years_ago=2, now=FALL),
                load_course(PROJECT1_EXPIRED, years_ago=1, now=FALL),
            ],
            3,
            FALL,
        ),
        (
            [
                load_course(ITGK_EXPIRED, years_ago=1, now=FALL),
                load_course(PROJECT1_ACTIVE, years_ago=0, now=FALL),
            ],
            2,
            FALL,
        ),
        ([load_course(ITGK_ACTIVE, years_ago=0, now=FALL)], 1, FALL),
    ],
)
def test_get_bachelor_year(groups, expected_year, application_time):
    assert expected_year == get_bachelor_year(groups, application_time)


@pytest.mark.parametrize(
    "feide_response,expected_year,expected_study",
    [
        ("1st_grader_2018", 1, FieldOfStudyType.BACHELOR),
        ("2nd_grader_2018", 2, FieldOfStudyType.BACHELOR),
        ("3rd_grader_2018", 3, FieldOfStudyType.BACHELOR),
        ("4th_grader_2018_dbs", 4, FieldOfStudyType.DATABASE_AND_SEARCH),
        ("4th_grader_2019_dbs", 4, FieldOfStudyType.DATABASE_AND_SEARCH),
        (
            "5th_grader_2018_ki",
            5,
            FieldOfStudyType.ARTIFICIAL_INTELLIGENCE,
        ),
        ("5th_grader_2018_pvs", 5, FieldOfStudyType.SOFTWARE_ENGINEERING),
        ("3rd_grader_extended_1_year_2018", 3, FieldOfStudyType.BACHELOR),
    ],
)
def test_find_study(feide_response, expected_year, expected_study):
    with open(DUMPS / f"{feide_response}.json") as f:
        groups = json.load(f)

    assert expected_study == get_field_of_study(groups)

    for application_time in [SPRING, FALL]:
        if expected_study == FieldOfStudyType.BACHELOR:
            assert expected_year == get_year(
                GROUP_IDENTIFIERS["BACHELOR"], groups, application_time
            )
        elif expected_study in FieldOfStudyType.ALL_MASTERS():
            assert expected_year == get_year(
                GROUP_IDENTIFIERS["MASTER"], groups, application_time
            )
        else:
            assert False

from django.test import TestCase

from ..courses import get_courses_for_key


class CoursesTestCase(TestCase):
    def test_get_courses_by_key(self):
        d = {
            "MASTER_COURSE": "",
            "MASTER_COURSE_1": "",
            "MASTER_COURSE_2": "",
            "BIT_COURSE_1": "",
        }

        self.assertEqual(2, len(get_courses_for_key(d, "MASTER_COURSE_")))

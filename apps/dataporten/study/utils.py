import logging

from dateutil.parser import parse
from django.utils import timezone

from apps.authentication.constants import FieldOfStudyType
from apps.dataporten.study.courses import GROUP_IDENTIFIERS, MASTER_IDS

logger = logging.getLogger(__name__)


def get_study(groups):
    study_group = {}
    for group in groups:
        if group.get('id') == GROUP_IDENTIFIERS['BACHELOR']:
            logger.debug('User found to be bachelor student')
            study_group = group
            break

        elif group.get('id') == GROUP_IDENTIFIERS['MASTER_OLD']:
            logger.debug('User found to be master student on old programme')
            study_group = group
            break

        elif group.get('id') == GROUP_IDENTIFIERS['MASTER']:
            logger.debug('User found to be master student')
            study_group = group
            break

    return study_group


def get_group_id(group):
    return group.get('id', '')


def get_group_name(group):
    return group.get('displayName', '')


def get_course_finish_date(course):
    if 'membership' in course:
        if 'notAfter' in course['membership']:
            # User has finished this course
            raw_datetime = course.get('membership', {}).get('notAfter', '')
            try:
                # Date format: 2014-08-14T22:00:00Z
                return parse(raw_datetime)
            except ValueError:
                logger.error('Failed to parse datetime "%s".' % raw_datetime)
    return None


def get_add_years(course):
    """Add years back for more recent courses.
        If course is 2nd grade, the user started one more year before."""
    # Add 1 year if verification happens during fall, 0 if during spring.
    add_years = 1 if timezone.now().month >= 7 else 0

    if course['id'] == GROUP_IDENTIFIERS['PROSJEKT1']:
        add_years += 1
    elif course['id'] == GROUP_IDENTIFIERS['ALGDAT']:
        add_years += 1
    elif course['id'] == GROUP_IDENTIFIERS['PROSJEKT2']:
        add_years += 3

    return min(3, add_years)


def get_year_from_course(course, date):
    return (timezone.now().year - date.year) + get_add_years(course)


def get_bachelor_year(groups):
    years = []
    for group in groups:
        if group.get('id') in GROUP_IDENTIFIERS.values():
            logger.debug('Finding study year from {}'.format(group.get('id')))
            parsed_datetime = get_course_finish_date(group)
            if parsed_datetime:
                years.append(get_year_from_course(group, parsed_datetime))
            else:
                # If we don't know the end date, only add the years for the course.
                years.append(get_add_years(group))

    return max(years)


def get_master_year(groups):
    for group in groups:
        if group.get('id') in MASTER_IDS:
            logger.debug('Identified master study course: %s' % group.get('id'))
            return 5
    return 4


def get_year(study_id, groups):
    if study_id == GROUP_IDENTIFIERS['BACHELOR']:
        return get_bachelor_year(groups)
    elif study_id == GROUP_IDENTIFIERS['MASTER']:
        return get_master_year(groups)
    else:
        return 0


def get_field_of_study(groups):
    if get_group_id(get_study(groups)) == GROUP_IDENTIFIERS['BACHELOR']:
        return FieldOfStudyType.BACHELOR
    else:
        found_master_study = False
        for group in groups:
            group_id = get_group_id(group)
            if group_id in (GROUP_IDENTIFIERS['MASTER_SPEC_PVS_OLD'], GROUP_IDENTIFIERS['MASTER_SPEC_SWE']):
                return FieldOfStudyType.SOFTWARE_ENGINEERING
            elif group_id in (GROUP_IDENTIFIERS['MASTER_SPEC_DBS_OLD'], GROUP_IDENTIFIERS['MASTER_SPEC_DBS']):
                return FieldOfStudyType.DATABASE_AND_SEARCH
            elif group_id in (GROUP_IDENTIFIERS['MASTER_SPEC_KI_OLD'], GROUP_IDENTIFIERS['MASTER_SPEC_AI']):
                return FieldOfStudyType.ARTIFICIAL_INTELLIGENCE
            elif group_id in (GROUP_IDENTIFIERS['MASTER_SPEC_UX_OLD'], GROUP_IDENTIFIERS['MASTER_SPEC_UX']):
                return FieldOfStudyType.INTERACTION_DESIGN
            elif group_id == GROUP_IDENTIFIERS['MASTER_COURSE_OTHER']:
                return FieldOfStudyType.OTHER_MASTERS
            elif group_id in (GROUP_IDENTIFIERS['MASTER'],  GROUP_IDENTIFIERS['MASTER_OLD']):
                found_master_study = True

        # If we don't find a specific master study, return 'other'
        if found_master_study:
            return FieldOfStudyType.OTHER_MASTERS

    # Return guest if we find nothing else
    return FieldOfStudyType.GUEST

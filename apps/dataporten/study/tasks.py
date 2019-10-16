import json
import logging
from datetime import datetime

import requests
from django.utils import timezone
from django.utils.http import urlencode

from apps.approval.models import MembershipApproval
from apps.approval.views import get_expiry_date
from apps.authentication.models import AllowedUsername, get_length_of_field_of_study
from apps.dataporten.study.utils import (
    get_field_of_study,
    get_group_id,
    get_study,
    get_year,
)

logger = logging.getLogger(__name__)


# API request functions

def fetch_groups_information(access_token, show_all=False):
    logger.debug('Fetching groups info...')
    query_params = urlencode({
        'show_all': show_all
    })
    groups_api = 'https://groups-api.dataporten.no/groups/me/groups?%s' % query_params
    groups_resp = requests.get(groups_api, headers={'Authorization': 'Bearer ' + access_token})
    return json.loads(groups_resp.content.decode(encoding='UTF-8'))


# Model changes

def find_user_study_and_update(user, groups):
    study_group = get_study(groups)
    study_id = get_group_id(study_group)
    study_year = get_year(study_id, groups)
    study_name = study_group.get('displayName')
    field_of_study = get_field_of_study(groups)

    # Remove the years from bachelor if the user is a master student.
    if study_year >= 4:
        start_date_for_study = study_year - 3
    else:
        start_date_for_study = study_year

    # Approvals are usually set from July 1st, so we do that here too.
    started_date = datetime(timezone.now().year - start_date_for_study + 1, 7, 1)

    logger.debug('Found {} to be studying {} on year {}'.format(user, study_id, study_year))

    if study_name:
        application = MembershipApproval.objects.create(
            applicant=user,
            approver=user,
            processed=True,
            processed_date=timezone.now(),
            approved=True,
            message='Automatisk godkjent gjennom integrasjon mot Dataporten.',
            field_of_study=field_of_study,
            new_expiry_date=get_expiry_date(started_date.year, get_length_of_field_of_study(field_of_study)),
            started_date=started_date,
        )

        if application.is_fos_application():
            user.field_of_study = application.field_of_study
            user.started_date = application.started_date
            user.save()

        if application.is_membership_application():
            membership = AllowedUsername.objects.filter(username=user.ntnu_username)
            if membership.count() == 1:
                membership = membership[0]
                if not membership.description:
                    membership.description = ''
                membership.description += """
                -------------------
                Updated by dataporten app.

                Automatically approved on %s.

                Old notes:
                %s
                """ % (str(timezone.now().date()), membership.note)
                membership.note = user.get_field_of_study_display() + " " + str(user.started_date)

            else:
                membership = AllowedUsername()
                membership.username = user.ntnu_username
                membership.registered = timezone.now().date()
                membership.description = """Added by dataporten app.

                Automatically approved on %s.""" % (str(timezone.now().date()))
                membership.note = user.get_field_of_study_display() + " " + str(user.started_date)

            membership.expiration_date = application.new_expiry_date
            logger.debug("ntnu username: ")
            logger.debug(user.ntnu_username)
            membership.save()

        return True, study_name, study_year


def set_ntnu_username(user, username):
    user.ntnu_username = username
    user.save()

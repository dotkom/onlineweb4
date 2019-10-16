import logging
import re
import time

import requests
from django.conf import settings

log = logging.getLogger('Slack')


class SlackException(Exception):
    pass


class SlackInvite:
    ERRORS = {
        'already_invited': 'E-posten har allerede blitt invitert',
        'invalid_auth': 'Klarte ikke sende invitasjon',
        'invalid_email': 'Ugyldig e-mail'
    }

    def __init__(self):
        self.token = settings.SLACK_INVITER['token']
        self.team_name = settings.SLACK_INVITER['team_name']

    def _url(self):
        return "https://{team}.slack.com/api/users.admin.invite?t={time}".format(
            team=self.team_name, time=int(time.time())
        )

    def _post(self, email):
        r = requests.post(self._url(), data={
            "email": email,
            "token": self.token,
            "set_active": "true",
            "_attempts": 1
        })
        if r.status_code != 200 or not isinstance(r.json(), dict):
            raise SlackException('Failed to invite user')
        data = r.json()
        if not data['ok']:
            raise SlackException(self._error_to_text(data['error']))

    def _match_email(self, email):
        return re.match(r'^.+@.+\..+', email)

    def invite(self, email):
        if not self._match_email(email):
            raise SlackException('Ugyldig e-mail')
        self._post(email)

    def _error_to_text(self, error_text):
        if error_text == 'invalid_auth':
            log.error('Auth to Slack API failed')
        if error_text in self.ERRORS:
            return self.ERRORS[error_text]
        log.warning('Unknown error from Slack API: ' + error_text)
        return 'Ukjent feilmelding'

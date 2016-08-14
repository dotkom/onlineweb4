import re
import time

import requests
from django.conf import settings


class SlackException(Exception):
    pass


class SlackInvite:
    def __init__(self):
        self.token = settings.SLACK_INVITER['token']
        self.team_name = settings.SLACK_INVITER['team_name']

    def _url(self):
        return "https://{team}.slack.com/api/users.admin.invite?t={time}".format(
            team=self.team_name, time=int(time.time())
        )

    def _post(self, email, name):
        r = requests.post(self._url(), data={
            "email": email,
            "first_name": name,
            "token": self.token,
            "set_active": "true",
            "_attempts": 1
        })
        if r.status_code != 200 or not isinstance(r.json(), dict):
            raise SlackException('Failed to invite user')
        data = r.json()
        if not data['ok']:
            raise SlackException(data['error'])

    def _match_email(self, email):
        return re.match(r'^.+@.+\..+', email)

    def invite(self, email, name):
        if not self._match_email(email):
            raise SlackException('Ugyldig e-mail')
        if name == '':
            raise SlackException('Ugyldig navn')
        self._post(email, name)

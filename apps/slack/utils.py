import re
import requests
import time

class SlackException(Exception):
    pass

class SlackInvite:
    def __init__(self):
        self.token = ''
        self.team_name = 'onlinentnu'
        self.channels = ['online']

    def _url(self):
        return "https://{team}.slack.com/api/users.admin.invite?t={time}".format(
            team=self.team_name, time=int(time.time())
        )

    def _post(self, email, name):
        r = requests.post(self._url(), data={
            "email": email,
            "first_name": name,
            "channels": self.channels,
            "token": self.token,
            "set_active": "true",
            "_attempts": 1
        })
        if r.status_code != 200 or not isinstance(r.data, dict):
            raise SlackException('Failed to invite user')
        if not r.data['ok']:
            raise SlackException(r.data['error'])

    def _match_email(self, email):
        return re.match(r'^.+@.+\..+', email)

    def invite(self, email, name):
        if not self._match_email(email):
            raise SlackException('Invalid e-mail')
        if name == '':
            raise SlackException('Empty name')
        self._post(email, name)

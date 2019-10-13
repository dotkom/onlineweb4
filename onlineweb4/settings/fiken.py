import os

from decouple import config

OW4_FIKEN_ORG = config('OW4_FIKEN_ORG', default='')
OW4_FIKEN_USER = config('OW4_FIKEN_USER', default='')
OW4_FIKEN_PASSWORD = config('OW4_FIKEN_PASSWORD', default='')

OW4_FIKEN_ACCOUNT_ARRKOM = config('OW4_FIKEN_ACCOUNT_ARRKOM', default='')
OW4_FIKEN_ACCOUNT_PROKOM = config('OW4_FIKEN_ACCOUNT_PROKOM', default='')
OW4_FIKEN_ACCOUNT_TRIKOM = config('OW4_FIKEN_ACCOUNT_TRIKOM', default='')
OW4_FIKEN_ACCOUNT_FAGKOM = config('OW4_FIKEN_ACCOUNT_FAGKOM', default='')

OW4_FIKEN_FILE_ROOT = config('OW4_FIKEN_FILE_ROOT', default=os.path.join('files', 'fiken', 'attachments'))

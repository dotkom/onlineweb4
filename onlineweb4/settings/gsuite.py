import os

from decouple import config

from .base import PROJECT_ROOT_DIRECTORY

OW4_GSUITE_CREDENTIALS_FILENAME = config('OW4_GSUITE_CREDENTIALS_FILENAME', default='gsuitecredentials.json')
OW4_GSUITE_CREDENTIALS_PATH = config('OW4_GSUITE_CREDENTIALS_PATH',
                                     default=os.path.join(PROJECT_ROOT_DIRECTORY, OW4_GSUITE_CREDENTIALS_FILENAME))

OW4_GSUITE_SETTINGS = {
    'CREDENTIALS': OW4_GSUITE_CREDENTIALS_PATH,
    'DOMAIN': config('OW4_GSUITE_SYNC_DOMAIN', default='online.ntnu.no'),
    # DELEGATED_ACCOUNT: G Suite Account with proper permissions to perform insertions and removals.
    'DELEGATED_ACCOUNT': config('OW4_GSUITE_DELEGATED_ACCOUNT', default=''),
    'ENABLED': config('OW4_GSUITE_ENABLED', cast=bool, default=False),
}

OW4_GSUITE_ACCOUNTS = {
    'ENABLED': config('OW4_GSUITE_ACCOUNTS_ENABLED', cast=bool, default=False),
    'ENABLE_INSERT': config('OW4_GSUITE_ACCOUNTS_ENABLE_INSERT', cast=bool, default=False),
}

OW4_GSUITE_SYNC = {
    'CREDENTIALS': OW4_GSUITE_SETTINGS.get('CREDENTIALS'),
    'DOMAIN': OW4_GSUITE_SETTINGS.get('DOMAIN'),
    'DELEGATED_ACCOUNT': OW4_GSUITE_SETTINGS.get('DELEGATED_ACCOUNT'),
    'ENABLED': config('OW4_GSUITE_SYNC_ENABLED', cast=bool, default=False),
    'ENABLE_INSERT': config('OW4_GSUITE_SYNC_ENABLE_INSERT', cast=bool, default=False),
    'ENABLE_DELETE': config('OW4_GSUITE_SYNC_ENABLE_DELETE', cast=bool, default=False),
    # OW4 name (lowercase) -> G Suite name (lowercase)
    'GROUPS': {
        'appkom': 'appkom',
        'arrkom': 'arrkom',
        'bankom': 'bankom',
        'bedkom': 'bedkom',
        'dotkom': 'dotkom',
        'ekskom': 'ekskom',
        'fagkom': 'fagkom',
        'fond': 'fond',
        'hovedstyret': 'hovedstyret',
        'jubkom': 'jubkom',
        'prokom': 'prokom',
        'seniorkom': 'seniorkom',
        'trikom': 'trikom',
        'tillitsvalgte': 'tillitsvalgte',
        'redaksjonen': 'redaksjonen',
        'itex': 'itex',
        'velkom': 'velkom',
        'interessegrupper': 'interessegrupper',
    }
}

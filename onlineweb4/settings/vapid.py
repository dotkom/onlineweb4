import os

from decouple import config

from .base import PROJECT_ROOT_DIRECTORY

OW4_VAPID_PRIVATE_KEY_FILENAME = config('OW4_VAPID_PRIVATE_KEY_FILENAME', default='vapid_private_key.pem')
OW4_VAPID_PRIVATE_KEY_PATH = config('OW4_VAPID_PRIVATE_KEY_PATH',
                                    default=os.path.join(PROJECT_ROOT_DIRECTORY, OW4_VAPID_PRIVATE_KEY_FILENAME))

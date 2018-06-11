from decouple import config

DATAPORTEN = {
    'STUDY': {
        'CLIENT_ID': config('OW4_DP_STUDY_CLIENT_ID', default=''),
        'CLIENT_SECRET': config('OW4_DP_STUDY_CLIENT_SECRET', default=''),
        'REDIRECT_URI': config('OW4_DP_STUDY_REDIRECT_URI', default=''),
        'PROVIDER_URL': 'https://auth.dataporten.no/oauth/token',
        'SCOPES': ['openid', 'userid', 'profile', 'groups', 'email'],
    }
}

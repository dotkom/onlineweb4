from decouple import config

DATAPORTEN = {
    "STUDY": {
        "ENABLED": config("OW4_DP_STUDY_ENABLED", cast=bool, default=False),
        "TESTING": config("OW4_DP_STUDY_TESTING", cast=bool, default=True),
        "CLIENT_ID": config("OW4_DP_STUDY_CLIENT_ID", default=""),
        "CLIENT_SECRET": config("OW4_DP_STUDY_CLIENT_SECRET", default=""),
        "REDIRECT_URI": config("OW4_DP_STUDY_REDIRECT_URI", default=""),
        "PROVIDER_URL": "https://auth.dataporten.no/oauth/token",
        "SCOPES": ["openid", "userid-feide", "profile", "groups", "email"],
    }
}

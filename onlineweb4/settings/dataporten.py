from decouple import config

DATAPORTEN = {
    "STUDY": {
        "TESTING": config("OW4_DP_STUDY_TESTING", cast=bool, default=True),
        "CLIENT_ID": config("OW4_DP_STUDY_CLIENT_ID", default=""),
        "CLIENT_SECRET": config("OW4_DP_STUDY_CLIENT_SECRET", default=""),
        "REDIRECT_URI": config("OW4_DP_STUDY_REDIRECT_URI", default=""),
        "PROVIDER_URL": "https://auth.dataporten.no/oauth/token",
        # userid-name gives access to extended userinfo https://docs.feide.no/reference/apis/extended_userinfo.html#example
        "SCOPES": [
            "openid",
            "userid-feide",
            "userid-name",
            "profile",
            "groups",
            "email",
        ],
    }
}

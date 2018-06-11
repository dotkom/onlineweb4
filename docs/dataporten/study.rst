Dataporten Study Integration
============================

Study
-----

The Study-integration towards Dataporten automatically determines eligibility for membership of Online through using the Dataporten Groups API.

To verify the eligibility of the user, OW4 requests information about all groups the user is part of on behalf of the user, through OAuth2-authorized requests.

OW4 determines which year and what the user studies based on the fetched groups.

Dataporten Groups API reference: https://docs.dataporten.no/docs/groups/
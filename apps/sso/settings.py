# -*- coding: utf8 -*-
#
# Created by 'myth' on 9/20/15


# SSO / OAuth2 settings
OAUTH2_SCOPES = {
    'null': 'Ingen datatilgang',
    'authentication.onlineuser.username.read': 'Brukernavn (Lesetilgang)',
    'authentication.onlineuser.first_name.read': 'Fornavn (Lesetilgang)',
    'authentication.onlineuser.last_name.read': 'Etternavn (Lesetilgang)',
    'authentication.onlineuser.email.read': 'Primær E-postaddresse (Lesetilgang)',
    'authentication.onlineuser.is_member.read': 'Medlemskapsstatus (Lesetilgang)',
    'authentication.onlineuser.field_of_study.read': 'Studieretning (Lesetilgang)',
    'authentication.onlineuser.nickname.read': 'Kallenavn (Lesetilgang)',
    'authentication.onlineuser.rfid.read': 'RFID (Lesetilgang)',
    'authentication.onlineuser.rfid.write': 'RFID (Skrivetilgang)',
}

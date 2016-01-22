# -*- coding: utf8 -*-
#
# Created by 'myth' on 9/20/15


# SSO / OAuth2 settings
OAUTH2_SCOPES = {
    'null': u'Ingen datatilgang',
    'read': u'DRF Read',
    'write': u'DRF Write',
    'authentication.onlineuser.username.read': u'Brukernavn (Lesetilgang)',
    'authentication.onlineuser.first_name.read': u'Fornavn (Lesetilgang)',
    'authentication.onlineuser.last_name.read': u'Etternavn (Lesetilgang)',
    'authentication.onlineuser.email.read': u'Primær E-postaddresse (Lesetilgang)',
    'authentication.onlineuser.is_member.read': u'Medlemskapsstatus (Lesetilgang)',
    'authentication.onlineuser.field_of_study.read': u'Studieretning (Lesetilgang)',
    'authentication.onlineuser.nickname.read': u'Kallenavn (Lesetilgang)',
    'authentication.onlineuser.rfid.read': u'RFID (Lesetilgang)',
    'authentication.onlineuser.rfid.write': u'RFID (Skrivetilgang)',
    'shop.readwrite': u'Tilgang til å endre en brukers saldo gjennom betalingssystemet (Lese og skrivetilgang)',
}

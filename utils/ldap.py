# -*- coding: utf8 -*-

import logging
from ldap3.utils.log import set_library_log_activation_level, EXTENDED, PROTOCOL, set_library_log_detail_level
from ldap3 import Server, Connection, ALL, SIMPLE, SYNC, ALL, NTLM, MODIFY_REPLACE, AUTH_SIMPLE, \
    SEARCH_SCOPE_WHOLE_SUBTREE, SEARCH_DEREFERENCE_ALWAYS, SUBTREE, SYNC, ALL_ATTRIBUTES
from ldap3.utils.conv import escape_bytes
from models import LdapGroup, LdapUser, LdapOrgUnit

logging.basicConfig(filename='client_application.log', level=logging.CRITICAL)
set_library_log_activation_level(logging.CRITICAL)
set_library_log_detail_level(EXTENDED)

MIN_UID = 2000

def upsert_user_ldap(user):
    """
    Update or Insert a user to LDAP

    :param user:
    :return:
    """

    # Check if user exists
    if exists(user):
        # User exists, update
        update(user)
    # New user, insert
    else:
        insert(user)


def exists(user):
    """
    Check if user exists in LDAP

    :param username: OnlineUser
    :param conn: Ldap connection
    :return: boolean exists
    """

    ldap_user = LdapUser.objects.filter(username=user.ntnu_username).first()
    return ldap_user not None


def update(user):
    """
    Update an existing user in LDAP

    :param user: OnlineUser
    :param changes: ldapmodify diff of changes
    :return: boolean updated
    """

    ldap_user = LdapUser.objects.filter(username=user.ntnu_username).first()
    ldap_user.username = user.ntnu_username
    ldap_user.email = user.ntnu_username + "@stud.ntnu.no"
    ldap_user.phone = user.phone_number
    ldap_user.first_name = user.first_name
    ldap_user.last_name = user.last_name
    ldap_user.save()

    # satisfy the return statement in comments
    return True;


def insert(user):
    """
    Insert a new user in LDAP

    :param user: OnlineUser
    :return: boolean inserted
    """

    # TODO: everything
    pass


def format_field(input):
    if input:
        return escape_bytes(input)
    else:
        return u'n/a'

def find_next_uid():
    # TODO: execute external script to find next UID
    # Or do the following: find the LdapUser with the highest
    # UID and add one
    # In that case: TODO: find unused UID if a user has been deleted
    if LdapUser.objects.exists():
        next_uid = LdapUser.objects.latest('uid').uid + 1
        if next_uid > MIN_UID: return next_uid
    return MIN_UID

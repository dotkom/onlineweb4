# -*- coding: utf8 -*-

from apps.ldap.ldap_models import LdapUser

MIN_UID = 2000


def upsert_user_ldap(user, pwd):
    """
    Update or Insert a user to LDAP

    :param user:
    :return:
    """

    # Check if user exists
    if exists(user):
        # User exists, update
        return update(user, pwd)
    # New user, insert
    else:
        return insert(user, pwd)


def exists(user):
    """
    Check if user exists in LDAP

    :param username: OnlineUser
    :param conn: Ldap connection
    :return: boolean exists
    """
    if not user.ntnu_username:
        return False

    # Get the user from ldap
    ldap_user = LdapUser.objects.filter(username=user.ntnu_username).first()
    return ldap_user is not None


def update(user, pwd):
    """
    Update an existing user in LDAP

    :param user: OnlineUser
    :param changes: ldapmodify diff of changes
    :return: boolean updated
    """
    try:
        # Update user
        ldap_user = LdapUser.objects.filter(username=user.ntnu_username).first()
        ldap_user.username = user.ntnu_username
        ldap_user.email = user.ntnu_username + "@stud.ntnu.no"
        ldap_user.phone = user.phone_number
        ldap_user.first_name = user.first_name
        ldap_user.last_name = user.last_name
        ldap_user.set_password(pwd)
        ldap_user.save()
        return True;
    except Exception:
        return False



def insert(user, pwd):
    """
    Insert a new user in LDAP

    :param user: OnlineUser
    :return: boolean inserted
    """

    # TODO: everything
    return False


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

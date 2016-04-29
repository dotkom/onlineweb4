# -*- coding: utf8 -*-

from apps.ldap.ldap_models import LdapUser, LdapGroup

MIN_UID = 2000

GROUP_MAP = {
    'arrKom': 'arrkom',
    'banKom': 'bankom',
    'bedKom': 'bedkom',
    'dotKom': 'dotkom',
    'fagKom': 'fagkom',
    'Hovedstyret': 'hovedstyret',
    'jubKom': 'jubkom',
    'Komiteer': 'komiteer',
    'proKom': 'prokom',
    'triKom': 'trikom',
}

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
        update_group_memberships(user)
        return True;
    except Exception:
        print("exception")
        return False



def insert(user, pwd):
    """
    Insert a new user in LDAP

    :param user: OnlineUser
    :return: boolean inserted
    """

    # TODO: everything
    return False

def update_group_memberships(user):
    ldap_groups = []
    for group in user.groups.all():
        if group.name in GROUP_MAP: ldap_groups.append(GROUP_MAP[group.name])

    # remove user from groups the user is no longer a member of
    for ldap_group in LdapGroup.objects.all():
        if not ldap_group.name in ldap_groups and user.ntnu_username in ldap_group.usernames:
            ldap_group.usernames.remove(user.ntnu_username)
            ldap_group.save()

    # add user to new groups
    for ldap_group in ldap_groups:
        group = LdapGroup.objects.filter(name=ldap_group).first()
        if not user.ntnu_username in group.usernames:
            group.usernames.append(user.ntnu_username)
            group.save()

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

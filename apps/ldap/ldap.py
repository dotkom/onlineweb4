# -*- coding: utf8 -*-
from logging import getLogger

from apps.ldap.ldap_models import LdapGroup, LdapUser

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
    'Redaksjonen': 'offline',
}

GROUP_PRIORITY = [
    'offline',
    'prokom',
]


def upsert_user_ldap(user, pwd=None):
    """
    Update or Insert a user to LDAP

    :param user: OnlineUser
    :param pwd: LDAP password
    :return: boolean successfull
    """

    if not user.ntnu_username:
        return False
    upsert_success = False

    try:
        ldap_user = LdapUser.objects.filter(username=user.ntnu_username).first()

        if ldap_user is not None:
            getLogger(__name__).debug('User exists, updating ldap...[username: %s, user_id: %s ,ldap_uid: %s]' % (
                ldap_user.username, user.id, ldap_user.uid))
            upsert_success = update(user)
        else:
            getLogger(__name__).debug(
                'User does not exist, inserting new in ldap... [username: %s, user_id: %s ,ldap_uid: %s]' % (
                    ldap_user.username, user.id, ldap_user.uid))
            upsert_success = insert(user)

        if pwd:
            getLogger(__name__).debug(
                'Updating internal services password ... [username: %s, user_id: %s ,ldap_uid: %s]' % (
                    ldap_user.username, user.id, ldap_user.uid))
            ldap_user = LdapUser.objects.filter(username=user.ntnu_username).first()
            ldap_user.set_password(pwd)

    except Exception as exception:
        getLogger(__name__).warning('Exception %s' % exception)
        print("ex %s" % exception)
        return False

    return upsert_success


def update(user):
    """
    Update an existing user in LDAP

    :param user: OnlineUser
    :param changes: ldapmodify diff of changes
    :return: boolean updated
    """

    # Update user
    try:
        ldap_user = LdapUser.objects.filter(username=user.ntnu_username).first()
        getLogger(__name__).debug('Found LDAP user %s' % ldap_user)
        ldap_user.username = user.ntnu_username
        ldap_user.email = user.ntnu_username + "@stud.ntnu.no"
        ldap_user.phone = user.phone_number
        ldap_user.first_name = user.first_name
        ldap_user.last_name = user.last_name
        getLogger(__name__).debug('Saving LDAP user %s' % ldap_user.username)
        ldap_user.save()
        update_group_memberships(user)
        getLogger(__name__).info('User %s successfully updated to LDAP' % ldap_user.username)
        return True
    except Exception as exception:
        getLogger(__name__).warning('[Updating User Info] Exception %s' % exception)
        return False


def insert(user):
    """
    Insert a new user in LDAP

    :param user: OnlineUser
    :param pwd: LDAP password
    :return: boolean inserted
    """

    try:
        getLogger(__name__).debug('Inserting LDAP user %s' % user.ntnu_username)
        ldap_user = LdapUser()
        ldap_user.first_name = user.first_name
        ldap_user.last_name = user.last_name
        ldap_user.full_name = user.get_full_name()
        ldap_user.email = user.ntnu_username + "@stud.ntnu.no"
        ldap_user.login_shell = '/bin/bash'
        ldap_user.username = user.ntnu_username
        ldap_user.uid = find_next_uid()
        ldap_user.group = get_primary_gid(user)
        ldap_user.home_directory = generate_home_path(ldap_user.username)
        getLogger(__name__).debug('Saving LDAP user %s' % ldap_user.username)
        ldap_user.save()
        update_group_memberships(user)
        getLogger(__name__).info('User %s successfully inserted to LDAP' % ldap_user.username)
        return True
    except Exception as exception:
        getLogger(__name__).warning('Exception %s' % exception)
        return False


def update_group_memberships(user):
    getLogger(__name__).debug('Updating group membership of %s' % user)
    ldap_groups = []
    for group in user.groups.all():
        if group.name in GROUP_MAP:
            ldap_groups.append(GROUP_MAP[group.name])

    # remove user from groups the user is no longer a member of
    for ldap_group in LdapGroup.objects.all():
        if ldap_group.name not in ldap_groups and user.ntnu_username in ldap_group.usernames:
            getLogger(__name__).debug('Removing %s from group %s ' % (user, ldap_group.name))
            ldap_group.usernames.remove(user.ntnu_username)
            ldap_group.save()

    # add user to new groups
    for ldap_group in ldap_groups:
        group = LdapGroup.objects.filter(name=ldap_group).first()
        if user.ntnu_username not in group.usernames:
            getLogger(__name__).debug('Adding %s to group %s' % (user, ldap_group))
            group.usernames.append(user.ntnu_username)
            group.save()


def find_next_uid():
    # TODO: execute external script to find next UID
    # Or do the following: find the LdapUser with the highest
    # UID and add one
    # In that case: TODO: find unused UID if a user has been deleted
    if LdapUser.objects.all().count() > 0:
        next_uid = LdapUser.objects.latest('uid').uid + 1
        print(str(LdapUser.objects.latest('uid')))
        if next_uid > MIN_UID:
            getLogger(__name__).debug('Setting UID to %s' % next_uid)
            return next_uid
    getLogger(__name__).debug('Setting UID to %s' % MIN_UID)
    return str(MIN_UID)


def generate_home_path(username):
    return '/home/' + username[:2] + '/' + username


def get_primary_gid(user):
    print("getting pri group")
    for group in user.groups.all():
        if group.name in GROUP_MAP:
            for i in range(0, len(GROUP_PRIORITY)):
                if GROUP_PRIORITY[i] == GROUP_MAP[group.name]:
                    LdapGroup.objects.filter(name=GROUP_MAP[group.name]).first().gid
    for group in user.groups.all():
        if group.name in GROUP_MAP:
            return LdapGroup.objects.filter(name=GROUP_MAP[group.name]).first().gid

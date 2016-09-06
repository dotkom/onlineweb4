# -*- coding: utf8 -*-

from logging import getLogger
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
    'Redaksjonen': 'offline',
}

GROUP_PRIORITY = [
    'offline',
    'prokom',
]


def upsert_user_ldap(user, pwd):
    """
    Update or Insert a user to LDAP

    :param user: OnlineUser
    :param pwd: LDAP password
    :return: boolean successfull
    """
    print("upsert in progress...")
    if not user.ntnu_username:
        print("no ntnu")
        return False

    try:
        print("trying hard")
        ldap_user = LdapUser.objects.filter(username=user.ntnu_username).first()
        if ldap_user is not None:
            print("ldap user is not none")
            getLogger(__name__).debug('User exists, updating...')
            return update(user, pwd)
        else:
            getLogger(__name__).debug('User does not exist, inserting...')
            print("inserting user")
            return insert(user, pwd)
    except Exception as exception:
        log.warning('Exception %s' % exception)
        print("ex %s" % exception)
        return False


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
        getLogger(__name__).debug('Found LDAP user %s' % ldap_user)
        ldap_user.username = user.ntnu_username
        ldap_user.email = user.ntnu_username + "@stud.ntnu.no"
        ldap_user.phone = user.phone_number
        ldap_user.first_name = user.first_name
        ldap_user.last_name = user.last_name
        ldap_user.set_password(pwd)
        getLogger(__name__).debug('Saving LDAP user %s' % ldap_user.username)
        ldap_user.save()
        update_group_memberships(user)
        getLogger(__name__).info('User %s successfully updated to LDAP' % ldap_user.username)
        return True
    except Exception as exception:
        log.warning('Exception ' + str(exception))
        return False


def insert(user, pwd):
    """
    Insert a new user in LDAP

    :param user: OnlineUser
    :param pwd: LDAP password
    :return: boolean inserted
    """

    try:
        getLogger(__name__).debug('Inserting LDAP user %s' % user.ntnu_username)
        print("inserting user")
        ldap_user = LdapUser()
        print("loL")
        ldap_user.first_name = user.first_name
        ldap_user.last_name = user.last_name
        ldap_user.full_name = user.get_full_name()
        ldap_user.email = user.ntnu_username + "@stud.ntnu.no"
        ldap_user.login_shell = '/bin/bash'
        ldap_user.username = user.ntnu_username
        ldap_user.uid = find_next_uid()
        ldap_user.group = get_primary_group(user)
        home_directory = generate_home_path(ldap_user.username)
        getLogger(__name__).debug('Saving LDAP user %s' % ldap_user.username)
        print("saving user")
        ldap_user.set_password(pwd)
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
        if not ldap_group.name in ldap_groups and user.ntnu_username in ldap_group.usernames:
            getLogger(__name__).debug('Removing %s from group %s ' % user, ldap_group.name)
            ldap_group.usernames.remove(user.ntnu_username)
            ldap_group.save()

    # add user to new groups
    for ldap_group in ldap_groups:
        group = LdapGroup.objects.filter(name=ldap_group).first()
        if not user.ntnu_username in group.usernames:
            getLogger(__name__).debug('Adding %s to group %s' % user, ldap_group.name)
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
        print(str(LdapUser.objects.latest('uid')))
        if next_uid > MIN_UID:
            getLogger(__name__).debug('Setting UID to %s' % next_uid)
            return next_uid
    getLogger(__name__).debug('Setting UID to %s' % MIN_UID)
    return str(MIN_UID)


def generate_home_path(username):
    return '/home/' + username[:2] + '/' + username


def get_primary_group(user):
    print("getting pri group")
    for group in user.groups.all():
        if group.name in GROUP_MAP:
            for i in range(0, len(GROUP_PRIORITY)):
                if GROUP_PRIORITY[i] == GROUP_MAP[group.name]:
                    return GROUP_MAP[group.name]
    for group in user.groups.all():
        if group.name in GROUP_MAP:
            return GROUP_MAP[group.name]

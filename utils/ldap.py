# -*- coding: utf8 -*-

import logging
from ldap3.utils.log import set_library_log_activation_level, EXTENDED, PROTOCOL, set_library_log_detail_level
from ldap3 import Server, Connection, ALL, SIMPLE, SYNC, ALL, NTLM, MODIFY_REPLACE, AUTH_SIMPLE, \
    SEARCH_SCOPE_WHOLE_SUBTREE, SEARCH_DEREFERENCE_ALWAYS, SUBTREE, SYNC, ALL_ATTRIBUTES
from ldap3.utils.conv import escape_bytes

logging.basicConfig(filename='client_application.log', level=logging.CRITICAL)
set_library_log_activation_level(logging.CRITICAL)
set_library_log_detail_level(EXTENDED)

# TODO:
# Dev now requires reverse ssh tunnel
host = 'localhost'
port = 9999

# Credentials
username = 'change_me'
password = 'change_me'

# Search args
default_args = 'dc=online,dc=ntnu,dc=no'


def upsert_user_ldap(user):
    """
    Update or Insert a user to LDAP

    :param user:
    :return:
    """

    # Setup Connection
    server = Server(host, port=port, use_ssl=False)

    # Connect
    conn = Connection(server, client_strategy=SYNC, authentication=SIMPLE, user=username, password=password)

    if not conn.bind():
        print('error in bind ' + conn.result)

    # Check if user exists
    if exists(user.username, conn):
        # User exists, update
        update(user, conn)
    # New user, insert
    else:
        insert(user, conn)

    # Close the connection
    conn.unbind()


def exists(username, conn):
    """
    Check if user exists in LDAP

    :param username: OnlineUser
    :param conn: Ldap connection
    :return: boolean exists
    """
    conn.search(search_base=default_args,
                search_filter='(&(objectClass=user)(sAMAccountName=' + format_field('read') + '))',
                search_scope=SUBTREE,
                attributes=['cn', 'name', 'sAMAccountName', 'givenName', 'mail'])

    if len(conn.entries) > 0:
        return True
    else:
        return False


def update(user, conn):
    """
    Update an existing user in LDAP

    :param user: OnlineUser
    :param conn: Ldap Connection
    :param changes: ldapmodify diff of changes
    :return: boolean updated
    """

    conn.modify('cn=' + user.username + ',cn=Users,' + default_args,
                {b'givenName': [(MODIFY_REPLACE, [b'rofl'])]})

    exists(user.username, conn)

    pass


def insert(user, conn):
    """
    Insert a new user in LDAP

    :param user: OnlineUser
    :param conn: Ldap Connection
    :return: boolean inserted
    """

    conn.add('cn=Users,' + default_args,
             attributes={'objectClass': ['user', 'organizationalPerson', 'person', 'top'],
                         'cn': format_field(user.username),
                         'sAMAccountName': format_field(user.username),
                         'name': format_field(user.username),
                         'mail': format_field(user.get_email()),
                         'sn': format_field(user.last_name),
                         'givenName': format_field(user.first_name)
                         })
    pass


def format_field(input):
    if input:
        return escape_bytes(input)
    else:
        return u'n/a'

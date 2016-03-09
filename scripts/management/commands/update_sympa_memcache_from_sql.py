#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
from memcache import Client

from django.core.management.base import NoArgsCommand

from onlineweb4.settings import SYMPA_DB_PASSWD, SYMPA_DB_USER, SYMPA_DB_NAME, SYMPA_DB_PORT, SYMPA_DB_HOST
from onlineweb4.settings import PUBLIC_LISTS


class Command(NoArgsCommand):
    def handle_noargs(self, **kwargs):
        self.update_mailinglists()

    def update_mailinglists(self):

        lists = []
        for pl in PUBLIC_LISTS:
            cur_list = {'name': pl, 'members': []}
            query = "select comment_subscriber,user_subscriber, reception_subscriber  from subscriber_table ' \
            'where list_subscriber = '%s' and reception_subscriber != 'nomail';" % pl

            db_con = psycopg2.connect(
                database=SYMPA_DB_NAME, host=SYMPA_DB_HOST, port=SYMPA_DB_PORT,
                user=SYMPA_DB_USER, password=SYMPA_DB_PASSWD
            )
            cursor = db_con.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            db_con.close()

            for row in rows:
                comment_subscriber, user_subscriber, reception_subscriber = row
                member = {}
                member['name'] = comment_subscriber
                member['subscriber'] = reception_subscriber
                member['email'] = user_subscriber
                cur_list['members'].append(member)

            lists.append(cur_list)

        mc = Client(["127.0.0.1:11211"], debug=0)
        mc.set("sympa_lists", lists)

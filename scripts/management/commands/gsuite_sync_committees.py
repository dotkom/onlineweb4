import logging

from django.conf import settings
from django.core.management import BaseCommand

from apps.gsuite.mail_syncer.main import update_g_suite_group
from apps.gsuite.mail_syncer.utils import (
    check_amount_of_members_ow4_g_suite,
    check_emails_match_each_other,
    get_g_suite_users_for_group,
    get_ow4_users_for_group,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        groups_to_sync = settings.OW4_GSUITE_SYNC.get("GROUPS")
        domain = settings.OW4_GSUITE_SYNC.get("DOMAIN")

        logger.info(
            "Starting sync of OW4 Groups' members to G Suite (domain: {}) with {}".format(
                domain, settings.OW4_GSUITE_SYNC.get("DELEGATED_ACCOUNT")
            )
        )
        logger.debug(f"Groups to be synced: {groups_to_sync}")

        for group in groups_to_sync:
            g_suite_users = get_g_suite_users_for_group(domain, group)
            ow4_users = get_ow4_users_for_group(group)
            logger.debug(f"Users in OW4: {ow4_users}")
            logger.debug(f"Users in G Suite: {g_suite_users}")

            should_update = False
            account_count_eq = check_amount_of_members_ow4_g_suite(
                g_suite_users, ow4_users
            )
            if not account_count_eq:
                logger.debug(
                    "Updating G Suite members since the number of members are inconsistent"
                )
                should_update = True
            else:
                logger.debug(
                    "Number of group members are equal, double checking email addresses"
                )
                should_update = not check_emails_match_each_other(
                    g_suite_users, ow4_users
                )

            if should_update:
                logger.info(f"Syncing {group}@{domain} with OW4 ...")
                update_g_suite_group(domain, group, g_suite_users, ow4_users)

            logger.info(f"{group}@{domain} is up to date with OW4.")

        logger.info("Done syncing OW4 with G Suite.")

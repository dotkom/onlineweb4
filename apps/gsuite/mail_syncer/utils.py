import logging

from django.conf import settings
from django.db.models import QuerySet
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from apps.authentication.models import OnlineUser as User
from apps.gsuite.auth import build_and_authenticate_g_suite_service

logger = logging.getLogger(__name__)

# Scopes for the directory API
scopes = [
    "https://www.googleapis.com/auth/admin.directory.group",
    "https://www.googleapis.com/auth/admin.directory.group.member",
    "https://www.googleapis.com/auth/admin.directory.user",
    "https://www.googleapis.com/auth/admin.directory.user.alias",
]


def setup_g_suite_client() -> Resource | None:
    """
    Sets up a working API client towards the Google Developers API.
    Requires various Django settings to be set to function properly.
    :return: Google API Client
    """
    if not settings.OW4_GSUITE_SYNC.get("ENABLED", False):
        logger.debug(
            "Trying to setup G Suite API client, but OW4_GSUITE_SYNC is not enabled."
        )
        return
    if not settings.OW4_GSUITE_SETTINGS.get("DELEGATED_ACCOUNT"):
        logger.error(
            "To be able to actually execute calls towards G Suite you must define DELEGATED_ACCOUNT."
        )
    if settings.OW4_GSUITE_SYNC.get("ENABLED") and (
        not settings.OW4_GSUITE_SYNC.get("ENABLE_INSERT")
        and not settings.OW4_GSUITE_SYNC.get("ENABLE_DELETE")
    ):
        logger.warning(
            "To be able to execute unsafe calls towards G Suite you must allow this in settings."
            'Neither "ENABLE_INSERT" nor "ENABLE_DELETE" are enabled.'
        )

    return build_and_authenticate_g_suite_service("admin", "directory_v1", scopes)


def get_group_key(domain: str, group_name: str) -> str:
    """
    Generates a group key to interact with the Google API.
    :param domain: Domain in which the group key should exist.
    :param group_name: Name of the group on a given domain to generate a key for.
    :return: The group key (groupname@domain)
    """
    if not domain or not group_name:
        logger.error(
            "You need to pass a domain and a group when generating group key.",
            extra={"domain": domain, "group": group_name},
        )
        raise ValueError(
            "You need to pass a domain and a group when generating group key."
        )

    email_domain = f"@{domain}"
    if email_domain in group_name:
        return group_name
    return f"{group_name}@{domain}"


def get_user_key(domain: str, user: User | str) -> str:
    """
    Generates a user key to interact with the Google API.
    :param domain: Domain in which the user key should exist.
    :param user: Unique property (e.g. primary email) of the user on a given domain to generate a key for.
    :return: The user key (email@domain)
    """
    if isinstance(user, str):
        if "@" in user:
            # If user is email address, return immediately.
            return user

    if not domain or not user:
        logger.error(
            "You need to pass a domain and a user when generating user key.",
            extra={"domain": domain, "group": user},
        )
        raise ValueError(
            "You need to pass a domain and a user when generating user key."
        )

    email_domain = f"@{domain}"
    if email_domain in user:
        return user
    return f"{user}{email_domain}"


def get_user(original_user: User, gsuite: bool = False, ow4: bool = False) -> User:
    """
    Returns the user of a given domain based on function parameters.
    Converts between OW4 users and G Suite users.
    :param original_user: The user to convert.
    :param gsuite: Set to True if you want a G Suite user returned.
    :param ow4: Set to True if you want an OW4 user returned.
    :return: User account for the given domain.
    """
    if not (gsuite or ow4):
        raise ValueError(
            "You need to pass either gsuite=True or ow4=True to cast user to that type."
        )

    gsuite_user = None
    ow4_user = None

    if isinstance(original_user, User):
        ow4_user = original_user
        gsuite_user = ow4_user.online_mail
    else:
        gsuite_user = original_user
        try:
            ow4_user = User.objects.get(online_mail__iexact=original_user)
        except User.DoesNotExist as err:
            logger.warning(f'User "{original_user}" does not exist on OW4!')
            raise err

    return ow4_user if ow4 else gsuite_user


def insert_email_into_g_suite_group(
    domain: str, group_name: str, email: str, suppress_http_errors: bool = False
):
    """
    Insert an email address into a G Suite group.
    :param domain: The domain in which to insert a user into.
    :param group_name: The name of the group the user should be inserted into.
    :param email: The email in question.
    :param suppress_http_errors: Whether or not to suppress HttpErrors happening during execution.
    :return: The response of the execution.
    """
    group_key = get_group_key(domain, group_name)

    logger.info(
        f"Inserting '{email}' into G Suite group '{group_key}'.",
        extra={"email": email, "group": group_key},
    )

    if not settings.OW4_GSUITE_SYNC.get("ENABLE_INSERT", False):
        logger.debug(
            f'Skipping inserting email "{email}" since ENABLE_INSERT is False.'
        )
        return

    g_suite_user_dict = {"email": get_user_key(domain, email), "role": "MEMBER"}

    directory = setup_g_suite_client()

    resp = None
    try:
        resp = (
            directory.members()
            .insert(body=g_suite_user_dict, groupKey=group_key)
            .execute()
        )
    except HttpError as err:
        logger.error(
            f"HttpError when inserting into G Suite group: {err}",
            extra={"suppress_http_error": suppress_http_errors},
        )
        if not suppress_http_errors:
            raise err
    logger.debug(f"Inserting response: {resp}")

    return resp


def insert_ow4_user_into_g_suite_group(
    domain: str, group_name: str, ow4_user: User, suppress_http_errors: bool = False
):
    """
    Insert a given OW4 user into a group in G Suite.
    :param domain: The domain in which to insert a user into.
    :param group_name: The name of the group the user should be inserted into.
    :param ow4_user: The OW4 user in question.
    :param suppress_http_errors: Whether or not to suppress HttpErrors happening during execution.
    :return: The response of the execution.
    """
    logger.info(
        f"Inserting '{ow4_user}' into G Suite group '{group_name}'.",
        extra={"user": ow4_user, "group": group_name},
    )

    if not ow4_user.online_mail:
        logger.error(
            f"OW4 User '{ow4_user}' ({ow4_user.pk}) missing Online email address! (current: '{ow4_user.online_mail}')",
            extra={"user": ow4_user, "group": group_name},
        )
        return

    return insert_email_into_g_suite_group(
        domain,
        group_name,
        ow4_user.online_mail,
        suppress_http_errors=suppress_http_errors,
    )


def remove_g_suite_user_from_group(
    domain: str,
    group_name: str,
    g_suite_user: dict | str,
    suppress_http_errors: bool = False,
):
    """
    Removes a user from a G Suite group.
    :param domain: The domain in which to remove a user from a group.
    :param group_name: The name of the group the user should be removed from.
    :param g_suite_user: The G Suite user in question.
    :param suppress_http_errors: Whether or not to suppress HttpErrors happening during execution.
    :return: The response of the execution.
    """
    if isinstance(g_suite_user, str):
        user_key = get_user_key(domain, g_suite_user)
    else:
        user_key = g_suite_user.get("email")
    if f"leder@{domain}" == user_key or f"nestleder@{domain}" == user_key:
        # Not removing these guys from any lists.
        logger.debug(
            f'Skipping removing user "{user_key}" since (s)he should be on all lists.'
        )
        return

    if not settings.OW4_GSUITE_SYNC.get("ENABLE_DELETE", False):
        logger.debug(
            f'Skipping removing user "{user_key}" since ENABLE_DELETE is False.'
        )
        return

    group_key = get_group_key(domain, group_name)

    directory = setup_g_suite_client()

    logger.info(
        f"Removing '{user_key}' from G Suite group '{group_key}'.",
        extra={"user": user_key, "group": group_key},
    )

    resp = None
    try:
        resp = (
            directory.members().delete(groupKey=group_key, memberKey=user_key).execute()
        )
    except HttpError as err:
        logger.error(
            f'HttpError when deleting user "{user_key}" from G Suite group: {err}',
            extra={"suppress_http_error": suppress_http_errors},
        )
        if not suppress_http_errors:
            raise err
    logger.debug(f"Removal of user response: {resp}")

    return resp


def get_g_suite_users_for_group(
    domain: str, group_name: str, suppress_http_errors: bool = False
):
    """
    Get the users in a given G Suite group.
    :param domain: The domain in which to find a groups user list.
    :param group_name: The name of the group to get group members for.
    :param suppress_http_errors: Whether or not to suppress HttpErrors happening during execution.
    :return: The response of the execution.
    """
    # G Suite Group Key
    group_key = get_group_key(domain, group_name)
    logger.debug(f"Getting G Suite member list for '{group_key}'.")

    directory = setup_g_suite_client()

    members = []
    try:
        members = directory.members().list(groupKey=group_key).execute().get("members")
    except HttpError as err:
        logger.error(
            f"HttpError when requesting user list: {err}",
            extra={"suppress_http_error": suppress_http_errors},
        )
        if not suppress_http_errors:
            raise err

    return members or []


def get_g_suite_groups_for_user(
    domain: str, _user: User, suppress_http_errors: bool = False
):
    """
    Get the group memberships for a given user.
    :param domain: The domain in which to find a users group memberships.
    :param _user: The user to get group memberships for.
    :param suppress_http_errors: Whether or not to suppress HttpErrors happening during execution.
    :type suppress_http_errors: bool
    :return: The response of the execution.
    """
    user = get_user(_user, gsuite=True)

    user_key = get_user_key(domain, user)
    logger.debug(
        f"Getting G Suite user membership list for '{user_key}'.",
        extra={"user": user_key},
    )

    directory = setup_g_suite_client()

    groups = []
    try:
        groups = directory.groups().list(userKey=user_key).execute().get("groups")
    except HttpError as err:
        logger.error(
            f"HttpError when requesting user group membership list: {err}",
            extra={"suppress_http_error": suppress_http_errors},
        )
        if not suppress_http_errors:
            raise err

    return groups or []


def get_ow4_users_for_group(group_name: str) -> QuerySet:
    """
    Get the OW4 group memberships for an OW4 user.
    :param group_name: The group name to match
    :return: A filtered QuerySet of Django groups the user is in.
    """
    return User.objects.filter(groups__name__iexact=group_name)


def get_appropriate_g_suite_group_names_for_user(domain: str, user: User) -> list[str]:
    """
    Get the G Suite groups a user should be in
    :param domain: The domain in which to get a users missing group memberships.
    :param user: The user to get group memberships for.
    :return: A list of appropriate G Suite group names.
    """
    g_suite_groups = settings.OW4_GSUITE_SYNC.get("GROUPS")
    user_groups = user.groups.all()
    g_suite_user_groups = []
    for group in user_groups:
        if group.name.lower() in g_suite_groups.keys():
            g_suite_user_groups.append(group.name.lower())

    return g_suite_user_groups


def get_missing_g_suite_group_names_for_user(domain: str, user: User) -> list[str]:
    """
    Generates a list of G Suite group names in which the user is not in, but should be.
    :param domain: The domain in which to get a users missing group memberships.
    :param user: The user to get group memberships for.
    :return: A list of names of the groups in which the user is not in, but should be in.
    """
    user_should_be_in_groups = get_appropriate_g_suite_group_names_for_user(
        domain, user
    )
    user_is_in_groups = [
        g.get("name").lower() for g in get_g_suite_groups_for_user(domain, user)
    ]

    missing_groups = []

    logger.debug(
        f'"{user}" is currently in "{user_is_in_groups}", should be in "{user_should_be_in_groups}".',
        extra={"user": user},
    )

    for group in user_should_be_in_groups:
        if group not in user_is_in_groups:
            missing_groups.append(group)

    return missing_groups


def get_excess_groups_for_user(domain: str, user: User) -> list[str]:
    """
    Generates a list of excess groups for a given user.
    :param domain: The domain in which to get a users excess group memberships.
    :param user: The user to get excess group memberships for.
    :return: A list of group names the user can be removed from.
    """
    user_should_be_in_groups = get_appropriate_g_suite_group_names_for_user(
        domain, user
    )
    user_is_in_groups = get_g_suite_groups_for_user(domain, user)
    available_groups = settings.OW4_GSUITE_SYNC.get("GROUPS").keys()

    excess_groups = []

    for group in user_is_in_groups:
        group_name = group.get("name").lower()
        # Make sure not to remove mailing list managers from lists they have to be in.
        if (
            group_name in available_groups
            and group_name not in user_should_be_in_groups
        ):
            excess_groups.append(group.get("name"))

    logger.info(f"{user} should be removed from these groups: {excess_groups}")
    return excess_groups


def check_amount_of_members_ow4_g_suite(
    g_suite_members: list[dict[str, str]],
    ow4_users: QuerySet[User],
    quiet: bool = False,
) -> bool:
    """
    Compare the number of users in an OW4 group to a G Suite group.
    :param g_suite_members: The members of a G Suite group.
    :param ow4_users: The members of an OW4 group.
    :param quiet: Whether to print debug log lines or not.
    :return: Whether or not there are exactly the same amount of users in the two groups.
    """
    g_suite_count = len(g_suite_members)
    ow4_count = ow4_users.count()
    if ow4_count == g_suite_count:
        return True
    elif g_suite_count > ow4_count:
        if not quiet:
            logger.debug(
                f"There are more users in G Suite ({g_suite_count}) than on OW4 ({ow4_count}). "
                "Need to trim inactive users from G Suite."
            )
    else:
        if not quiet:
            logger.debug(
                f"There are more users on OW4 ({ow4_count}) than in G Suite ({g_suite_count}). "
                "Need to update G Suite with new members."
            )
    return False


def check_emails_match_each_other(
    g_suite_users: list[dict[str, str]], ow4_users: QuerySet[User]
) -> bool:
    """
    Matches emails in two lists of users against each other.
    :param g_suite_users: The members of a G Suite group.
    :param ow4_users: The members of an OW4 group.
    :return: Whether or not all emails in the two groups exactly match each other.
    """
    if not check_amount_of_members_ow4_g_suite(g_suite_users, ow4_users, quiet=True):
        return False

    logger.debug("Verifying that all users match to an email address.")
    for gsuite_user, ow4_user in zip(
        g_suite_users, ow4_users.order_by("first_name"), strict=False
    ):
        if ow4_user.online_mail != gsuite_user.get("email"):
            logger.debug(
                f"Emails do not match! '{ow4_user.online_mail}' != '{gsuite_user.get('email')}'"
            )
            return False
    return True


def get_excess_users_in_g_suite(
    g_suite_users: list[dict[str, str]], ow4_users: QuerySet
) -> list[dict[str, str]]:
    """
    Finds excess users from lists of G Suite users and OW4 users.
    :param g_suite_users: The members of a G Suite group.
    :param ow4_users: The members of an OW4 group.
    :return: A list of excess users.
    """
    excess_users = []

    for user in g_suite_users:
        try:
            ow4_users.get(online_mail=user.get("email").split("@")[0])
        except User.DoesNotExist:
            excess_users.append(user)

    logger.debug(f"Excess users in G Suite: {excess_users}")

    return excess_users


def _get_g_suite_user_from_g_suite_user_list(
    g_suite_users: list[dict[str, str]], g_suite_email: str
) -> dict[str, str] | None:
    """
    Tries to find a user from a list of users, matching a given email address.
    :param g_suite_users: The members of a G Suite group.
    :param g_suite_email: The email address to match.
    :return: The user matching the email address, if any.
    """
    for user in g_suite_users:
        if g_suite_email == user.get("email"):
            logger.debug(f"Found user with G Suite email address '{g_suite_email}'")
            return user
    logger.debug(f"Could not find user with G Suite email address '{g_suite_email}'")
    return None


def get_missing_ow4_users_for_g_suite(
    g_suite_users: list[dict[str, str]], users: QuerySet[User]
) -> list[dict[str, str]]:
    """
    Find the OW4 users who are missing given a set of G Suite users.
    :param g_suite_users: The members of a G Suite group.
    :param ow4_users: The members of an OW4 group.
    :return: A list of users missing from the given G Suite user set.
    """
    missing_users = []
    domain = settings.OW4_GSUITE_SYNC.get("DOMAIN")

    for user in users:
        if not _get_g_suite_user_from_g_suite_user_list(
            g_suite_users, f"{user.online_mail}@{domain}"
        ):
            missing_users.append(user)

    logger.debug(
        f"OW4 users missing in G Suite ({len(missing_users)}): {missing_users}"
    )
    return missing_users

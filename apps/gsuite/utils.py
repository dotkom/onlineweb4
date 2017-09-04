import logging

logger = logging.getLogger(__name__)


def get_group_key(domain, group_name):
    """
    Generates a group key to interact with the Google API.
    :param domain: Domain in which the group key should exist.
    :type domain: str
    :param group_name: Name of the group on a given domain to generate a key for.
    :type group_name: str
    :return: The group key (groupname@domain)
    :rtype: str
    """
    if not domain or not group_name:
        logger.error('You need to pass a domain and a group when generating group key.',
                     extra={'domain': domain, 'group': group_name})
        raise ValueError('You need to pass a domain and a group when generating group key.')

    email_domain = "@{domain}".format(domain=domain)
    if email_domain in group_name:
        return group_name
    return '{group}@{domain}'.format(group=group_name, domain=domain)


def get_user_key(domain, user):
    """
    Generates a user key to interact with the Google API.
    :param domain: Domain in which the user key should exist.
    :type domain: str
    :param group_name: Unique property (e.g. primary email) of the user on a given domain to generate a key for.
    :type group_name: str
    :return: The user key (email@domain)
    :rtype: str
    """
    if isinstance(user, str):
        if '@' in user:
            # If user is email address, return immediately.
            return user

    if not domain or not user:
        logger.error('You need to pass a domain and a user when generating user key.',
                     extra={'domain': domain, 'group': user})
        raise ValueError('You need to pass a domain and a user when generating user key.')

    email_domain = "@{domain}".format(domain=domain)
    if email_domain in user:
        return user
    return "{user_email}{email_domain}".format(user_email=user, email_domain=email_domain)

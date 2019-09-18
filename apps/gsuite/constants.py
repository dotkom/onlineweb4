class GsuiteRoleType:
    """
    Types of group members for Gsuite groups.
    Gives different sets of access right to the members
    """
    """ 
    This role is only available if the Google Groups for Business is enabled using the Admin console.
    A MANAGER role can do everything done by an OWNER role except make a member an OWNER or delete the group.
    A group can have multiple MANAGER members.
    """
    MANAGER = 'MANAGER'
    """
    This role can subscribe to a group, view discussion archives, and view the group's membership list
    """
    MEMBER = 'MEMBER'
    """
    This role can send messages to the group, add or remove members, change member roles, change group's settings,
    and delete the group. An OWNER must be a member of the group. A group can have more than one OWNER.
    """
    OWNER = 'OWNER'

    ALL_CHOICES = (
        (MANAGER, 'Manager'),
        (MEMBER, 'Medlem'),
        (OWNER, 'Eier'),
    )
    ALL_TYPES = [t for t, v in ALL_CHOICES]

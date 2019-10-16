from django.contrib.auth.models import Group


def has_view_all_perms(user):
    return (
        user in Group.objects.get(name="dotKom").user_set.all()
        or user in Group.objects.get(name="proKom").user_set.all()
    )


def has_view_perms(user, poster):
    return (
        user in Group.objects.get(name="dotKom").user_set.all()
        or user in Group.objects.get(name="proKom").user_set.all()
        or user in poster.ordered_committee.user_set.all()
        or user == poster.ordered_by
    )


def has_edit_perms(user, *args):
    return (
        user in Group.objects.get(name="proKom").user_set.all()
        or user in args[0].ordered_committee.user_set.all()
    )

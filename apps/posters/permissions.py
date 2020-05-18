from apps.authentication.models import OnlineUser as User

from .models import Poster


def has_view_all_perms(user: User) -> bool:
    has_global_perm = user.has_perm("posters.view_poster_order")
    return has_global_perm


def has_view_perms(user: User, poster: Poster) -> bool:
    has_global_perm = user.has_perm("posters.view_poster_order")
    has_object_perm = user.has_perm("posters.view_poster_order", poster)
    return has_global_perm or has_object_perm


def has_edit_perms(user: User, poster: Poster):
    has_global_perm = user.has_perm("posters.change_poster")
    has_object_perm = user.has_perm("posters.change_poster", poster)
    return has_global_perm or has_object_perm

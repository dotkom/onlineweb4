import json

from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404

from apps.authentication.constants import RoleType
from apps.authentication.models import GroupMember, GroupRole, OnlineGroup
from apps.authentication.models import OnlineUser as User


def handle_group_member_remove(
    request: HttpRequest, group: OnlineGroup
) -> HttpResponse:
    resp = {"status": 200}
    user = get_object_or_404(User, pk=int(request.POST["user_id"]))
    member = get_object_or_404(GroupMember, user=user, group=group)
    member.delete()
    user_ids = group.members.values_list("user_id")
    users = User.objects.filter(pk__in=user_ids)
    message = f"{user.get_full_name()} ble fjernet fra {group.name_long}"

    resp["message"] = message
    resp["users"] = [{"user": u.get_full_name(), "id": u.id} for u in users]
    resp["users"].sort(key=lambda x: x["user"])

    return HttpResponse(json.dumps(resp), status=200)


def handle_group_member_add(request: HttpRequest, group: OnlineGroup) -> HttpResponse:
    resp = {"status": 200}
    user = get_object_or_404(User, pk=int(request.POST["user_id"]))
    full_name = user.get_full_name()
    try:
        member = GroupMember.objects.create(group=group, user=user)
        member_role = GroupRole.get_for_type(RoleType.MEMBER)
        member.roles.add(member_role)
        user_ids = group.members.values_list("user_id")
        users = User.objects.filter(pk__in=user_ids)

        resp["full_name"] = full_name
        resp["users"] = [{"user": u.get_full_name(), "id": u.id} for u in users]
        resp["users"].sort(key=lambda x: x["user"])
        resp["message"] = f"{full_name} ble lagt til i {group.name_long}"

        return HttpResponse(json.dumps(resp), status=200)
    except IntegrityError:
        return HttpResponse(
            f"{full_name} er allerede i gruppen {group.name_long}", status=400
        )

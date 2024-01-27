# API v1
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.inventory.models import Item
from apps.shop.forms import SetRFIDForm
from apps.shop.models import MagicToken, OrderLine
from apps.shop.serializers import ItemSerializer, UserOrderLineSerializer


class UserOrderViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    serializer_class = UserOrderLineSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return OrderLine.objects.filter(user=self.request.user)


class InventoryViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin
):
    queryset = Item.objects.filter(available=True).order_by("pk")
    serializer_class = ItemSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


@method_decorator(login_required, name="dispatch")
class SetRFIDWebView(FormView):
    form_class = SetRFIDForm
    template_name = "shop/set_rfid.html"
    success_url = reverse_lazy("home")

    def get(self, request, token="", *args, **kwargs):
        get_object_or_404(MagicToken, token=token)
        return super().get(request, token, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs["current_rfid"] = self.request.user.rfid
        kwargs["token"] = self.kwargs.get("token")
        return super().get_context_data(**kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial["rfid"] = MagicToken.objects.get(token=self.kwargs.get("token")).data
        return initial

    def post(self, request, token="", *args, **kwargs):
        logger = logging.getLogger(__name__)
        form = self.get_form()
        if not form.is_valid():
            return self.form_invalid(form)

        if not token:
            form.add_error("Det finnes ingen token i denne forespørselen.")
            return self.form_invalid(form)

        magictoken = None
        try:
            magictoken = MagicToken.objects.get(token=token)
        except MagicToken.DoesNotExist:
            form.add_error("Tokenet du prøver å bruke eksisterer ikke.")
            return self.form_invalid(form)

        old_rfid = magictoken.user.rfid
        magictoken.user.rfid = magictoken.data
        magictoken.user.save()

        logger.debug(
            '{authed_user} updated RFID for {user} (from "{old}" to "{new}").'.format(
                authed_user=self.request.user,
                user=magictoken.user,
                old=old_rfid,
                new=magictoken.data,
            )
        )

        magictoken.delete()

        messages.success(request, "Oppdaterte RFID for {}".format(magictoken.user))
        return self.form_valid(form)

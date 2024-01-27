from django.urls import reverse


class GetUrlMixin:
    basename = ""

    def get_action_url(self, action: str, id=None):
        if id:
            return reverse(f"{self.basename}-{action}", args=[id])
        return reverse(f"{self.basename}-{action}")

    def get_list_url(self):
        return self.get_action_url("list")

    def get_detail_url(self, id):
        return self.get_action_url("detail", id)

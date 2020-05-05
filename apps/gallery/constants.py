from django.db.models import TextChoices


class ImageFormat(TextChoices):
    ARTICLE = "article", "Artikkel"
    COMPANY = "company", "Bedriftslogo"
    EVENT = "event", "Arrangement"
    OFFLINE = "offline", "Offline"
    PHOTOALBUM = "photoalbum", "Fotoalbum"
    PRODUCT = "product", "Produktbilde"
    RESOURCE = "resource", "Ressurs"
    GROUP = "group", "Gruppe"

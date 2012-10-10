from django.contrib import admin
from models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_display = ("heading", "ingress")

admin.site.register(Article, ArticleAdmin)

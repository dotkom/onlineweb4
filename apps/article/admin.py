from django.contrib import admin
from models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_display = ("heading", "created_by", "changed_by")

    #set the created and changed by fields
    def save_model(self, request, obj, form, change): 
        obj.changed_by = request.user
        if not change:
            obj.created_by = request.user
        obj.save()

admin.site.register(Article, ArticleAdmin)

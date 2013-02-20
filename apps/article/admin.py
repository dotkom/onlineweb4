from django.contrib import admin
from apps.article.models import Article, Tag, ArticleTag
from django.conf import settings

class ArticleTagAdmin(admin.ModelAdmin):
    model = ArticleTag

class ArticleTagInline(admin.TabularInline):
    model = ArticleTag
    max_num = 99
    extra = 0

class TagAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        if not change:
            obj.created_by = request.user
        obj.save()

class ArticleAdmin(admin.ModelAdmin):
    # Defining sizes for crop used by filebrowser
    #ADMIN_VERSIONS = getattr(settings, 'FILEBROWSER_ADMIN_VERSIONS', ['article_main', 'article_front_featured', 'article_front_small'])
    #ADMIN_THUMBNAIL = getattr(settings, 'FILEBROWSER_ADMIN_THUMBNAIL', 'admin_thumbnail')
    
    inlines = (ArticleTagInline,)
    list_display = ("heading", "created_by", "changed_by")

    #set the created and changed by fields
    def save_model(self, request, obj, form, change): 
        obj.changed_by = request.user
        if not change:
            obj.created_by = request.user
        obj.save()
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instances in instances:
            instances.save()
    
admin.site.register(Article, ArticleAdmin)
admin.site.register(Tag, TagAdmin)

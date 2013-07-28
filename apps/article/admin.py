from django.contrib import admin
from apps.article.models import Article, Tag, ArticleTag
from django.conf import settings
from filebrowser.settings import VERSIONS, ADMIN_THUMBNAIL

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
    inlines = (ArticleTagInline,)
    list_display = ("heading", "created_by", "changed_by")

    #set the created and changed by fields
    def save_model(self, request, obj, form, change): 
        if (obj.image):
            obj.image.version_generate(ADMIN_THUMBNAIL).url
            
            # Itterate the different versions (by key)
            for ver in VERSIONS.keys():
                # Check if the key start with article_ (if it does, we want to crop to that size)
                if ver.startswith('article_'):
                    obj.image.version_generate(ver).url
            
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

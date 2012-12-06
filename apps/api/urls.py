from django.conf.urls import patterns, url, include

from tastypie.api import Api

from apps.article.api import ArticleResource
from apps.events.api import EventResource
from apps.marks.api import MarkResource, EntryResource, MyMarksResource, MyActiveMarksResource
from apps.userprofile.api import UserResource

v0_api = Api(api_name='v0')

# userprofile
v0_api.register(UserResource())

# event
v0_api.register(EventResource())

# article
v0_api.register(ArticleResource())

# marks
v0_api.register(MarkResource())
v0_api.register(EntryResource())
v0_api.register(MyMarksResource())
v0_api.register(MyActiveMarksResource())



# Set the urls to be included.
urlpatterns = patterns('',
    url(r'^',       include(v0_api.urls)),
)

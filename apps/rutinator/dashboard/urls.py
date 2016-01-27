from django.conf.urls import patterns, url
from apps.rutinator.dashboard.views import TaskListView, CreateTaskView, EditTaskView

urlpatterns = patterns(
    'apps.rutinator.dashboard.views',
    url(r'^$', TaskListView.as_view(), name='task_view'),
    url(r'^create/$', CreateTaskView.as_view(), name='task_create'),
    url(r'^edit/(?P<pk>\d+)/$', EditTaskView.as_view(), name='task_edit')
)


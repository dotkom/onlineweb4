from apps.dashboard.tools import DashboardMixin
from django.views.generic import ListView
from apps.rutinator.models import Task

class TaskListView(DashboardMixin, ListView):
    model = Task
    queryset = Task.objects.all()
    template_name = "rutinator/dashboard/index.html"


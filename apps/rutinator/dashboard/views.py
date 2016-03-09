from apps.dashboard.tools import DashboardMixin
from django.views.generic import ListView, UpdateView, CreateView
from apps.rutinator.models import Task
from apps.rutinator.dashboard.forms import NewTaskForm
from django.core.urlresolvers import reverse_lazy

class TaskListView(DashboardMixin, ListView):
    model = Task
    queryset = Task.objects.all()
    template_name = "rutinator/dashboard/index.html"

class CreateTaskView(DashboardMixin, CreateView):
    model = Task
    form_class = NewTaskForm
    template_name = 'rutinator/dashboard/create.html'
    success_url = reverse_lazy('dashboard:task_view')

class EditTaskView(DashboardMixin, UpdateView):
    model = Task
    form_class = NewTaskForm
    template_name = 'rutinator/dashboard/edit.html'
    success_url = reverse_lazy('dashboard:task_view')



from copy import copy
from tastypie.resources import ModelResource
from models import Event

class EventResource(ModelResource):

    def alter_list_data_to_serialize(self, request, data):
        # Rename list data object to 'events'.
        if isinstance(data, dict):
            data['events'] = copy(data['objects'])
            del(data['objects'])
        return data

    class Meta:
        queryset = Event.objects.all()
        resource_name = 'events'

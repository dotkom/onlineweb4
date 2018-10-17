import six
from rest_framework.pagination import PageNumberPagination as RFPageNumberPagination


class PageNumberPagination(RFPageNumberPagination):
    page_size = 10
    max_page_size = 80
    
    def get_page_size(self, request):
        if 'size' in request.query_params:
            return min(self.max_page_size, int(request.query_params['size']))
        return self.page_size
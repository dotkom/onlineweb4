# -*- coding: utf-8 -*-
import logging

try:
    from zappa.asynchronous import task
except ImportError:
    # Zappa is only required if we are running on Lambda
    def task(func):
        return func


from apps.gallery.util import create_responsive_image_from_file

from .models import Issue
from .utils import pdf_page_to_png

logger = logging.getLogger(__name__)


def create_thumbnail(offline_issue: Issue):
    with pdf_page_to_png(pdf=offline_issue.issue, page_number=0) as thumbnail_file:
        responsive_image = create_responsive_image_from_file(
            file=thumbnail_file,
            name=f"{offline_issue.title} - forsidebilde",
            description=f"Forsidebilde for {offline_issue.title}",
            photographer="Bildegeneratoren for Offline",
            preset="offline",
        )
        offline_issue.image = responsive_image
        offline_issue.save()


@task
def create_thumbnail_task(issue_id: int):
    offline_issue = Issue.objects.get(pk=issue_id)
    create_thumbnail(offline_issue)

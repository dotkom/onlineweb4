# -*- coding: utf-8 -*-
import logging

from onlineweb4.celery import app

from apps.gallery.util import create_responsive_image_from_file

from .models import Issue
from .utils import pdf_page_to_png

logger = logging.getLogger(__name__)


def create_thumbnail(offline_issue: Issue):
    thumbnail_file = pdf_page_to_png(pdf=offline_issue.issue, page_number=0)
    responsive_image = create_responsive_image_from_file(
        file=thumbnail_file,
        name=f"{offline_issue.title} - forsidebilde",
        description=f"Forsidebilde for {offline_issue.title}",
        photographer="Bildegeneratoren for Offline",
        preset="offline",
    )
    offline_issue.image = responsive_image
    offline_issue.save()


@app.task(bind=True)
def create_thumbnail_task(_, issue_id: int):
    offline_issue = Issue.objects.get(pk=issue_id)
    create_thumbnail(offline_issue)

import uuid
from tempfile import gettempdir

import fitz
from django.core.files.storage import default_storage
from django.db.models.fields.files import FieldFile
from django.core.files.storage import default_storage


def pdf_page_to_png(pdf: FieldFile, page_number=0):
    """
    Creates a PNG image of the first page of a PDF
    """
    source_pdf = fitz.open(stream=default_storage.open(pdf.name).read(), filetype="pdf")
    first_page: fitz.Page = source_pdf[page_number]
    first_page_image = first_page.getPixmap(alpha=False, matrix=fitz.Matrix(4.0, 4.0))

    temp_image_path = f"{gettempdir()}/{uuid.uuid1()}.png"
    first_page_image.writePNG(temp_image_path)
    image_file = open(temp_image_path, "rb")

    return image_file

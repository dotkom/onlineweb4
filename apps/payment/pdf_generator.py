from textwrap import wrap
import uuid

from pdfdocument.utils import PDFDocument
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, TableStyle
from tempfile import gettempdir


class FikenSalePDF:

    def __init__(self, sale):
        self.sale = sale
        self.table_data = [(
            create_body_text('Vare'),
            create_body_text('Pris'),
        )]
        self.create_table_data()

    def create_table_data(self):
        for order_line in self.sale.order_lines.all():
            price = order_line.price / 100
            self.table_data.append((
                create_body_text(order_line.description),
                create_body_text(f'{price} kr')
            ))

    @property
    def column_widths(self):
        return 285, 185

    def render_pdf(self):
        path = f'{gettempdir()}/{uuid.uuid1()}'
        pdf = PDFDocument(path)
        pdf.init_report()

        pdf.p('Kvittering for kjøp på online.ntnu.no', style=create_paragraph_style(font_size=18))
        pdf.spacer(10)
        pdf.p(self.sale.created_date.strftime('%d. %B %Y'), create_paragraph_style(font_size=9))
        pdf.spacer(height=25)

        pdf.p('Ordrelinjer', style=create_paragraph_style(font_size=14))
        pdf.spacer(height=20)
        pdf.table(self.table_data, self.column_widths, style=get_table_style())
        pdf.spacer(height=25)

        pdf.generate()
        pdf_file = open(path, 'r')
        return pdf_file


# Table style for framed table with grids
def get_table_style(full_spans=None):
    style = [
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
    ]
    if full_spans:
        for line in full_spans:
            style.append(('SPAN', (0, line), (-1, line)))

    return TableStyle(style)


# Normal paragraph
def create_paragraph_style(font_name='Helvetica', font_size=10, color=colors.black):
    style = getSampleStyleSheet()['Normal']
    style.fontSize = font_size
    style.fontName = font_name
    style.textColor = color

    return style


# Paragraph with word-wrapping, useful for tables
def create_body_text(text, font_name='Helvetica', font_size=10, color=colors.black):
    style = getSampleStyleSheet()['BodyText']
    style.fontSize = font_size
    style.fontName = font_name
    style.textColor = color

    return Paragraph(text, style=style)

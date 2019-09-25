import uuid
from tempfile import gettempdir

from pdfdocument.utils import PDFDocument
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, TableStyle


class FikenSalePDF:

    def __init__(self, sale):
        self.sale = sale
        self.table_data = [(
            create_body_text('Vare'),
            create_body_text('Mva'),
            create_body_text('Pris'),
        )]
        self.create_table_data()

    def create_table_data(self):
        for order_line in self.sale.order_lines.all():
            self.table_data.append((
                create_body_text(order_line.description),
                create_body_text(f'{order_line.vat_percentage * 100} %'),
                create_body_text(f'{ order_line.price / 100} kr')
            ))

    @property
    def column_widths(self):
        return 245, 80, 145

    def render_pdf(self):
        path = f'{gettempdir()}/{uuid.uuid1()}'
        pdf = PDFDocument(path)
        pdf.init_report()

        pdf.p('Kvittering for kjøp på online.ntnu.no', style=create_paragraph_style(font_size=18))
        pdf.spacer(10)
        pdf.p(self.sale.created_date.strftime('%d. %B %Y'), create_paragraph_style(font_size=9))
        pdf.spacer(height=25)

        pdf.p('Linjeforeningen Online', style=create_paragraph_style(font_size=13))
        pdf.spacer(height=6)
        pdf.p('992 548 045 MVA', style=create_paragraph_style(font_size=11))

        pdf.spacer(height=25)
        pdf.p('Ordrelinjer', style=create_paragraph_style(font_size=14))
        pdf.spacer(height=20)
        pdf.table(self.table_data, self.column_widths, style=get_table_style())

        pdf.spacer(height=25)
        pdf.p('Total', style=create_paragraph_style(font_size=14))
        pdf.spacer(height=10)

        pdf.p(f'{self.sale.original_amount / 100} kr', style=create_paragraph_style(font_size=12))

        pdf.generate()
        pdf_file = open(path, 'rb')
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

import logging
import uuid
from tempfile import gettempdir

from django.conf import settings
from pdfdocument.utils import PDFDocument
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, TableStyle

logger = logging.getLogger(__name__)

ONLINE_LOGO_IMAGE = (
    f"{settings.PROJECT_ROOT_DIRECTORY}/files/static/img/online_logo_blue.png"
)

HEADER = "Kvittering for kjøp på online.ntnu.no"
ORG_NAME = "Linjeforeningen Online"
ORG_CODE = "992 548 045 MVA"


def format_nok_value(amount: int) -> str:
    str_value = str(amount)
    return f"{str_value[:-2]},{str_value[-2:]} kr"


class FikenSalePDF:
    def __init__(self, sale):
        self.sale = sale

    @property
    def order_line_table_data(self):
        table_data = [["Vare", "Mva", "Pris"]]
        for order_line in self.sale.order_lines.all():
            table_data.append(
                [
                    order_line.description,
                    f"{order_line.vat_percentage * 100} %",
                    format_nok_value(order_line.net_price),
                ]
            )

        return table_data

    @property
    def vat_table_data(self):
        order_lines_by_vat = {}
        for order_line in self.sale.order_lines.all():
            if order_line.vat_percentage not in order_lines_by_vat:
                order_lines_by_vat[order_line.vat_percentage] = []
            order_lines_by_vat[order_line.vat_percentage].append(order_line)

        vat_totals = []
        for vat_percentage, order_lines in order_lines_by_vat.items():
            total_for_vat = sum([line.net_price for line in order_lines])
            vat_totals.append(
                [None, f"{vat_percentage} %", format_nok_value(total_for_vat)]
            )

        return vat_totals

    @property
    def column_widths(self):
        return 320, 60, 90

    def render_pdf(self):
        path = f"{gettempdir()}/{uuid.uuid1()}"
        pdf = PDFDocument(path)
        pdf.init_report()

        online_logo = Image(filename=ONLINE_LOGO_IMAGE)
        online_logo.drawWidth /= 8
        online_logo.drawHeight /= 8
        pdf.append(online_logo)
        pdf.spacer(height=25)

        pdf.p(HEADER, style=create_paragraph_style(font_size=18))
        pdf.spacer(height=16)
        pdf.p(
            self.sale.created_date.strftime("%d. %B %Y %H:%M"),
            create_paragraph_style(font_size=9),
        )
        pdf.p(
            f"Kvitteringsnummer: K{self.sale.id}", create_paragraph_style(font_size=9)
        )
        pdf.spacer(height=25)

        pdf.p(ORG_NAME, style=create_paragraph_style(font_size=13))
        pdf.spacer(height=6)
        pdf.p(ORG_CODE, style=create_paragraph_style(font_size=11))

        pdf.spacer(height=15)
        pdf.p("Mottaker", style=create_paragraph_style(font_size=13))
        pdf.spacer(height=6)
        pdf.p(
            self.sale.customer.user.get_full_name(),
            style=create_paragraph_style(font_size=11),
        )

        pdf.spacer(height=25)
        pdf.p("Ordrelinjer", style=create_paragraph_style(font_size=14))
        pdf.spacer(height=20)
        table_style = get_order_line_table_style(line_color=colors.dimgrey)
        pdf.table(self.order_line_table_data, self.column_widths, style=table_style)

        pdf.spacer(height=20)
        pdf.p("Moms", style=create_paragraph_style(font_size=14))
        pdf.spacer(height=10)
        vat_table_type = get_vat_table_style(line_color=colors.dimgrey)
        pdf.table(self.vat_table_data, self.column_widths, style=vat_table_type)

        pdf.spacer(height=25)
        pdf.p("Total", style=create_paragraph_style(font_size=14))
        pdf.spacer(height=10)

        pdf.p(
            format_nok_value(self.sale.amount),
            style=create_paragraph_style(font_size=12),
        )

        pdf.generate()
        pdf_file = open(path, "rb")
        return pdf_file


def get_vat_table_style(full_spans=None, line_color=colors.grey):
    style = [
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, line_color),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ]
    if full_spans:
        for line in full_spans:
            style.append(("SPAN", (0, line), (-1, line)))

    return TableStyle(style)


# Table style for framed table with grids
def get_order_line_table_style(full_spans=None, line_color=colors.grey):
    style = [
        ("LINEBELOW", (0, 0), (-1, 0), 1, line_color),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, line_color),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ]
    if full_spans:
        for line in full_spans:
            style.append(("SPAN", (0, line), (-1, line)))

    return TableStyle(style)


# Normal paragraph
def create_paragraph_style(font_name="Helvetica", font_size=10, color=colors.black):
    style = getSampleStyleSheet()["Normal"]
    style.fontSize = font_size
    style.fontName = font_name
    style.textColor = color

    return style


# Paragraph with word-wrapping, useful for tables
def create_body_text(text, font_name="Helvetica", font_size=10, color=colors.black):
    style = getSampleStyleSheet()["BodyText"]
    style.fontSize = font_size
    style.fontName = font_name
    style.textColor = color

    return Paragraph(text, style=style)

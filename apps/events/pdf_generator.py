# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required, user_passes_test

from pdfdocument.utils import pdf_response
from reportlab.platypus import TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

class EventPDF:

    event = None
    attendees = None
    waiters = None
    attendee_table_data = None
    waiters_table_data = None
    allergies_table_data = None

    def __init__(self, event):
        self.event = event
        self.attendees = sorted(event.attendance_event.attendees.all()[:event.attendance_event.max_capacity], key=lambda attendee: attendee.user.last_name)
        self.waiters = event.wait_list
        self.attendee_table_data = [(u'Navn', u'Klasse', u'Studie', u'Telefon'), ]
        self.waiters_table_data = [(u'Navn', u'Klasse', u'Studie', u'Telefon'), ]
        self.allergies_table_data = []

        self.create_attendees_table_data()
        self.create_waiters_table_data()
        

    # Create table data for attendees with a spot
    def create_attendees_table_data(self):

        for attendee in self.attendees:
            user = attendee.user
            self.attendee_table_data.append((create_body_text("%s, %s" % (user.last_name, user.first_name)),
                                             user.year, create_body_text(user.get_field_of_study_display()),
                                             user.phone_number))

            if user.allergies:
                self.allergies_table_data = self.allergies_table_data + [user.first_name + ' ' + user.last_name  + ': ' + user.allergies]

    # Create table data for attendees waiting for a spot
    def create_waiters_table_data(self):

        for attendee in self.waiters:
            user = attendee.user
            self.waiters_table_data.append((create_body_text("%s, %s" % (user.last_name, user.first_name)),
                                            user.year, create_body_text(user.get_field_of_study_display()),
                                            user.phone_number))

            if user.allergies:
                self.allergies_table_data = self.allergies_table_data + [user.first_name + ' ' + user.last_name  + ': ' + user.allergies]

    def attendee_column_widths(self):
        return (185, 40, 170, 75)

    def allergies_column_widths(self):
        return (200, 200)

    def render_pdf(self):
        pdf, response = pdf_response(self.event.title + u" attendees")
        pdf.init_report()

        pdf.p(self.event.title, style=create_paragraph_style(font_size=18))
        pdf.spacer(10)
        pdf.p(self.event.event_start.strftime('%d. %B %Y'), create_paragraph_style(font_size=9))
        pdf.spacer(height=25)

        pdf.p(u"Påmeldte", style=create_paragraph_style(font_size=14))
        pdf.spacer(height=20)
        pdf.table(self.attendee_table_data, self.attendee_column_widths(), style=get_table_style())
        pdf.spacer(height=25)

        pdf.p(u"Venteliste", style=create_paragraph_style(font_size=14))
        pdf.spacer(height=20)
        pdf.table(self.waiters_table_data, self.attendee_column_widths(), style=get_table_style())
        pdf.spacer(height=25)

        pdf.p(u"Allergier", style=create_paragraph_style(font_size=14))
        pdf.spacer(height=12)
        pdf.ul(self.allergies_table_data)

        pdf.generate()
        return response


# Table style for framed table with grids
def get_table_style():
    return TableStyle(
        [
            ('GRID',(0,0),(-1,-1),0.5,colors.grey),
            ('BOX',(0,0),(-1,-1),1,colors.black),
        ]
    )

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
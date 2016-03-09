# -*- coding: utf-8 -*-

from textwrap import wrap

from pdfdocument.utils import pdf_response
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, TableStyle


class EventPDF(object):

    event = None
    attendees = None
    waiters = None
    reservees = None
    attendee_table_data = None
    waiters_table_data = None
    reservee_table_data = None
    allergies_table_data = None

    def __init__(self, event):
        self.event = event
        attendee_qs = event.attendance_event.attendees_qs
        self.attendees = sorted(attendee_qs, key=lambda attendee: attendee.user.last_name)
        self.waiters = event.attendance_event.waitlist_qs
        self.reservees = event.attendance_event.reservees_qs
        self.attendee_table_data = [('Navn', 'Klasse', 'Studie', 'Telefon'), ]
        self.waiters_table_data = [('Navn', 'Klasse', 'Studie', 'Telefon'), ]
        self.reservee_table_data = [('Navn', 'Notat'), ]
        self.allergies_table_data = [('Allergisk mot', 'Navn'), ]

        self.full_span_attendee_lines = []
        self.full_span_waiters_lines = []
        self.create_attendees_table_data()
        self.create_waiters_table_data()
        self.create_reservees_table_data()

    # Create table data for attendees with a spot
    def create_attendees_table_data(self):
        i = 1

        for attendee in self.attendees:
            user = attendee.user
            self.attendee_table_data.append((
                                            create_body_text("%s, %s" % (user.last_name, user.first_name)),
                                            user.year,
                                            create_body_text(user.get_field_of_study_display()),
                                            user.phone_number
                                            ))

            if attendee.note:
                self.attendee_table_data.append(
                    (create_body_text('Notat for %s: ' % attendee.user.first_name + attendee.note),))
                i += 1
                self.full_span_attendee_lines.append(i)
            if user.allergies:
                # Breaks the line every 60th character
                allergies = "\n".join(wrap(user.allergies, width=60))
                self.allergies_table_data.append((allergies, user.get_full_name(),))

            i += 1

    # Create table data for attendees waiting for a spot
    def create_waiters_table_data(self):
        i = 1

        for attendee in self.waiters:
            user = attendee.user
            self.waiters_table_data.append((
                create_body_text("%s, %s" % (user.last_name, user.first_name)),
                user.year,
                create_body_text(user.get_field_of_study_display()),
                user.phone_number
            ))

            if attendee.note:
                self.waiters_table_data.append(
                    (create_body_text('Notat for %s: ' % attendee.user.first_name + attendee.note),))
                i += 1
                self.full_span_waiters_lines.append(i)
            if user.allergies:
                # Breaks the line every 60th character
                allergies = "\n".join(wrap(user.allergies, width=60))
                self.allergies_table_data.append((allergies, user.get_full_name(),))

            i += 1

    def create_reservees_table_data(self):
        for reservee in self.reservees:
            self.reservee_table_data.append((
                create_body_text(reservee.name),
                create_body_text(reservee.note)
            ))
            if reservee.allergies:
                self.allergies_table_data.append((
                    create_body_text(reservee.allergies),
                    create_body_text(reservee.name),
                ))
                if reservee.allergies:
                    # self.allergies_table_data = self.allergies_table_data + [reservee.name + ' ' + reservee.allergies]
                    pass

    def attendee_column_widths(self):
        return 185, 40, 170, 75

    def reservee_column_widths(self):
        return 185, 285

    def allergies_column_widths(self):
        return 285, 185

    def render_pdf(self):
        pdf, response = pdf_response(self.event.title + " attendees")
        pdf.init_report()

        pdf.p(self.event.title, style=create_paragraph_style(font_size=18))
        pdf.spacer(10)
        pdf.p(self.event.event_start.strftime('%d. %B %Y'), create_paragraph_style(font_size=9))
        pdf.spacer(height=25)

        pdf.p("Påmeldte", style=create_paragraph_style(font_size=14))
        pdf.spacer(height=20)
        pdf.table(self.attendee_table_data, self.attendee_column_widths(),
                  style=get_table_style(self.full_span_attendee_lines))
        pdf.spacer(height=25)

        if self.waiters.count() > 0:
            pdf.p("Venteliste", style=create_paragraph_style(font_size=14))
            pdf.spacer(height=20)
            pdf.table(self.waiters_table_data, self.attendee_column_widths(),
                      style=get_table_style(self.full_span_waiters_lines))
            pdf.spacer(height=25)

        if self.reservees and self.reservees.count() > 0:
            pdf.p("Reservasjoner", style=create_paragraph_style(font_size=14))
            pdf.spacer(height=20)
            pdf.table(self.reservee_table_data, self.reservee_column_widths(), style=get_table_style())
            pdf.spacer(height=25)

        if self.allergies_table_data:
            pdf.p("Allergier", style=create_paragraph_style(font_size=14))
            pdf.spacer(height=20)
            pdf.table(self.allergies_table_data, self.allergies_column_widths(), style=get_table_style())
            pdf.spacer(height=25)

        pdf.generate()
        return response


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

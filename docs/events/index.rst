######
Events
######


.. toctree::
   :maxdepth: 2

   api

All types of events require the :class:`~apps.events.models.Event` class.
For a description of the fields see the API reference,
but at the core an event is just a title, image, describing text and start/end times.

**************
Company Events
**************

Some events are a collaboration with companies.
To assign a company to an event create a :class:`~apps.events.models.CompanyEvent`.
More than one company can be assigned to an event by creating several :class:`~apps.events.models.CompanyEvent`.

By creating a relation to a company a couple of things happen:

- The company's logo is used as the event image
- A link to the company is added to the event description page

*****************
Attendance events
*****************

Some events require users to sign up before attending. :class:`~apps.events.models.AttendanceEvent` implements the functionality for this.
An AttendanceEvent is connected to an Event by a :class:`django.db.models.OneToOneField`.

Attendancee events adds the following features:

- Registration start/end
- Limited number of attendee seats
- Waitlist
- PDF/JSON attendee lists(for organizing committee)
- Sending emails to attendees
- Postponed registration because of marks

In addition to the features above some features can be added after creating an attendance event:

Extras
======

Originally created to allow choosing between pizza and sushi, but has later been used for a variety of food choices.
When adding extras the user is presented with a dropdown box after signing up for the event.

Enabled by creating an instance of :class:`~apps.events.models.Extras`.

Group Restriction
=================

Some events are limited to members of a few specific groups.
For all other users the event is hidden and can not be signed up for.
This has traditionally been used for the annual committee Christmas party.

Enabled by creating an instance of :class:`~apps.events.models.GroupRestriction` with event and groups specified.


Feedback
========

See :ref:`feedback`.

Payment
=======

See :ref:`payment events<payment-events>`.

Reservation
===========

Some events have external attendees which are handled manually by the organizers.
By adding a :class:`~apps.events.models.Reservation` a specified number of seats are marked as taken on the event.
To the user these seats will always look like they are taken,
but the organizers can manually fill these seats by creating instances of :class:`apps.events.models.Reservee`.

Typically used for events like Immball.


Rule Based Access Control
=========================

By default all events are accessible for all members. See :ref:`approval` for details on what a member is.



Limitations: Unable to set specific number of seats per rule.

*Disclaimer: author of this documentation(Duvholt) has never worked on this code, so some details might be wrong.*


Rule(Base Class)
----------------

Implements helper methods for checking offset.

All rules inherit from this rule.

See :class:`~apps.events.models.Rule`.

Field of Study Rule
-------------------

Limit attendance to field of study with offset. E.g. bachelor students or "Programvaresystemer".

See :class:`~apps.events.models.FieldOfStudyRule`.

Grade Rule
----------

Limit attendance to specified grade with offset. E.g. 1st year students only, or 2nd year students after 24 hours.

See :class:`~apps.events.models.GradeRule`.

User Group Rule
---------------

At the time of writing this rule has not been used.

See :class:`~apps.events.models.UserGroupRule`.

*TODO: Fint out why GroupRestriction was created instead.*

Rule Bundle
-----------

Used to bundle different rules together. This was intended to make it easier to create an event as many of the rules are reused. 

An example of a rule bundle:

- 1-3 year students after 24 hours(Grade rule)
- All master students(several field of study rules)
- PhD(Field of study rule)

See :class:`~apps.events.models.RuleBundle`.

Unfortunately over time the list of rule bundles have grown more than expected because of weird combinations.

*******
Archive
*******

A list of all events can be found in the archive.

It is possible to search and filter on future events only or events the user has attended.

***************
Calendar Export
***************

Events can be exported as iCalendar(ics).
Calendars like Google Calendar will automatically update the calendar when new events are added. 

Three different types of calendar export is supported:

- All events(public)
- User events(private)
- Specific event(public)

The private calendar is implemented using Django's signing tool :class:`django.core.signing.Signer` with username as key.

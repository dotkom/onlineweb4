class NotificationType:
    EVENT_REGISTRATION = 'event_registration'
    EVENT_UPDATES = 'event_updates'
    EVENT_WAIT_LIST_BUMP = 'event_wait_list_bump'
    EVENT_FEEDBACK_CREATED = 'feedback_created'

    ARTICLE_CREATED = 'article_created'
    OFFLINE_CREATED = 'offline_created'

    ANNOUNCEMENT = 'announcement'
    COMMITTEE_ANNOUNCEMENT = 'committee_announcement'

    WINE_PUNISHMENT = 'wine_punishment'

    ALL_CHOICES = (
        (EVENT_REGISTRATION, 'Arrangementspåmeldinger'),
        (EVENT_UPDATES, 'Arrangementsoppdateringer'),
        (EVENT_WAIT_LIST_BUMP, 'Oppdatering av venteliste'),
        (EVENT_FEEDBACK_CREATED, 'Tilbakemeldingsskjemaer'),
        (ARTICLE_CREATED, 'Nye artikler'),
        (OFFLINE_CREATED, 'Nye Offline'),
        (ANNOUNCEMENT, 'Oppdateringer fra Online'),
        (COMMITTEE_ANNOUNCEMENT, 'Oppdateringer for komiteer'),
        (WINE_PUNISHMENT, 'Vinstraffer'),
    )

    ALL_TYPES = [option[0] for option in ALL_CHOICES]

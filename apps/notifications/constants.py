from django.db.models import TextChoices

# Small badge used as the app-icon. Shown at the top bar of an android phone.
# variable: badge
NOTIFICATION_BADGE_URL = "https://beta.online.ntnu.no/static/owf-badge-128.png"

# Used as the app icon for notifications
# variable: icon
DEFAULT_NOTIFICATION_ICON_URL = "https://beta.online.ntnu.no/static/pwa-icon-v0-192.png"

# The vibration rhythm to use for the notification
# variable: vibrate
NOTIFICATION_VIBRATION_PATTERN = [
    500,
    110,
    500,
    110,
    450,
    110,
    200,
    110,
    170,
    40,
    450,
    110,
    200,
    110,
    170,
    40,
    500,
]

# Tune played when the notification is triggered
# variable: sound
NOTIFICATION_SOUND = ""


class PermissionType(TextChoices):
    """
    Choices a user can make for what they want to be notified about
    """

    #
    DEFAULT = "DEFAULT", "Standard varslinger"
    GROUP_MESSAGE = "GROUP_MESSAGE", "Meldinger til grupper du er med i"

    # Applications
    APPLICATIONS = "APPLICATIONS", "Søknader (medlemskap- og komitésøknader)"

    # Articles
    ARTICLE_CREATED = "ARTICLE_CREATED", "Nye artikler"

    # Events
    REGISTRATION_OPENING = "REGISTRATION_OPENING", "Påmeldingsstart"
    WAIT_LIST_BUMP = "WAIT_LIST_BUMP", "Opprykk fra venteliste"
    REGISTERED_BY_ADMIN = "REGISTERED_BY_ADMIN", "Påmeldt av administrator"

    # Marks
    NEW_MARK = "NEW_MARK", "Ny prikk"
    MARK_RULES_UPDATED = "MARK_RULES_UPDATED", "Oppdatering av prikkereglene"

    # Offline
    OFFLINE_CREATED = "OFFLINE_CREATED", "Nye utgaver av Offline"

    # Payments
    RECEIPT = "RECEIPT", "Kvitteringer"

from django.db.models import IntegerChoices


class AttendStatus:
    REGISTER_SUCCESS = "10"

    PREVIOUSLY_REGISTERED = "20"

    ON_WAIT_LIST = "30"
    USER_NOT_ATTENDING = "31"

    RFID_DOES_NOT_EXIST = "40"
    USERNAME_AND_RFID_MISSING = "41"
    EVENT_ID_MISSING = "42"

    USERNAME_DOES_NOT_EXIST = "50"
    REGISTER_ERROR = "51"

    NOT_LOGGED_IN = "60"
    NOT_AUTHORIZED = "61"
    EVENT_DOES_NOT_EXIST = "62"


class EventType:
    SOSIALT = 1
    BEDPRES = 2
    KURS = 3
    UTFLUKT = 4
    EKSKURSJON = 5
    INTERNT = 6
    ANNET = 7
    KJELLEREN = 8

    ALL_CHOICES = (
        (SOSIALT, "Sosialt"),
        (BEDPRES, "Bedriftspresentasjon"),
        (KURS, "Kurs"),
        (UTFLUKT, "Utflukt"),
        (EKSKURSJON, "Ekskursjon"),
        (INTERNT, "Internt"),
        (ANNET, "Annet"),
        (KJELLEREN, "Realfagskjelleren"),
    )


class RegisterStatus(IntegerChoices):
    # Allowed status codes
    ALLOWED_MEMBERS = 200, "Tillatt for alle medlemmer."
    ALLOWED_GUEST = 201, "Tillatt for alle medlemmer og gjester."

    # Allowed by bundle types (21x)
    ALLOWED_FOS_RULE = 210, "Tillatt gjennom studieretning."
    ALLOWED_GRADE_RULE = 211, "Tillatt gjennom årskull."
    ALLOWED_GROUP_RULE = 212, "Tillatt gjennom gruppe."
    ALLOWED_GENERIC_RULE = 213, "Tillatt gjennom regler."

    # Blocked status codes (4xx)
    BLOCKED_MEMBERS_ONLY = 400, "Dette arrangementet er kun åpent for medlemmer."
    BLOCKED_MARK = 401, "Din påmelding er utsatt grunnet prikk."
    BLOCKED_NOT_OPEN_YET = 402, "Påmeldingen har ikke åpnet enda."
    BLOCKED_NO_ACCESS = (
        403,
        "Du har ikke tilgang til å melde deg på dette arrangementet.",
    )
    BLOCKED_IS_ATTENDING = 404, "Du er allerede meldt på dette arrangementet."
    BLOCKED_SUSPENSION = 405, "Du er suspendert og kan ikke melde deg på."

    # Blocked by rule (41x)
    BLOCKED_FOS_RULE = (
        410,
        "Din studieretning har ikke tilgang til dette arrangementet.",
    )
    BLOCKED_GRADE_RULE = (
        411,
        "Ditt klassetrinn har ikke tilgang til dette arrangementet.",
    )
    BLOCKED_GROUP_RULE = (
        412,
        "Dine brukergrupper har ikke tilgang til dette arrangementet.",
    )
    BLOCKED_GENERIC_RULE = 413, "Du har ikke tilgang til å melde deg på arrangementet."

    # Blocked by postponed registration (42x)
    POSTPONED_FOS_RULE = 420, "Din studieretning har utsatt påmelding."
    POSTPONED_GRADE_RULE = 421, "Ditt klassetrinn har utsatt påmelding."
    POSTPONED_GROUP_RULE = 422, "Dine brukergrupper har utsatt påmelding."
    POSTPONED_GENERIC_RULE = 423, "Du har utsatt påmelding."

    # Error status codes
    ERROR_REGISTRATION_CLOSED = 502, "Påmeldingen er ikke lenger åpen."
    ERROR_NO_SEATS_LEFT = 503, "Det er ikke mer plass på dette arrangementet."

    @staticmethod
    def is_allowed(status: "RegisterStatus"):
        return 200 <= status.value < 300

    @staticmethod
    def is_postponed(status: "RegisterStatus"):
        return 420 <= status.value < 430

    @staticmethod
    def is_blocked(status: "RegisterStatus"):
        return 400 <= status.value < 500

    @staticmethod
    def is_error(status: "RegisterStatus"):
        return 500 <= status.value

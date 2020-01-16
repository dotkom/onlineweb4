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

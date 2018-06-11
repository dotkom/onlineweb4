import json

from django.utils import timezone


def load_course(course, active=False, years_ago=0):
    if active and years_ago != 0:
        raise ValueError('Cannot have a course in the present be active.')
    elif active:
        return course
    year = timezone.now().year - years_ago
    print('creating course %s years ago in year %s (now is %s)' % (years_ago, year, timezone.now().year))
    return json.loads(json.dumps(course) % str(year))


# Studies

LAST_YEAR = timezone.now().year - 1
NEXT_YEAR = timezone.now().year + 1
# @ToDo: Set year based on expected course year
# @ToDo: Build list of courses based on year student?

INFORMATICS_BACHELOR_STUDY_PROGRAMME = json.loads("""{
        "url": "http://www.ntnu.no/studier/bit",
        "type": "fc:fs:prg",
        "displayName": "Informatikk - bachelorstudium",
        "parent": "fc:org:ntnu.no",
        "membership": {
            "basic": "member",
            "active": true,
            "fsroles": [
                "STUDENT"
            ],
            "displayName": "Student"
        },
        "id": "fc:fs:fs:prg:ntnu.no:BIT"
    }""")

INFORMATICS_MASTER_STUDY_PROGRAMME = json.loads("""{
        "url": "http://www.ntnu.no/studier/mit",
        "type": "fc:fs:prg",
        "displayName": "Informatikk - masterstudium",
        "parent": "fc:org:ntnu.no",
        "membership": {
            "basic": "member",
            "active": true,
            "fsroles": [
                "STUDENT"
            ],
            "displayName": "Student"
        },
        "id": "fc:fs:fs:prg:ntnu.no:MIT"
    }""")

INFORMATICS_MASTER_PVS_SPECIALIZATION = json.loads("""{
        "type": "fc:fs:str",
        "parent": "fc:org:ntnu.no",
        "membership": {
            "basic": "member",
            "active": true,
            "fsroles": [
                "STUDENT"
            ],
            "displayName": "Student"
        },
        "id": "fc:fs:fs:str:ntnu.no:MIT-PVS",
        "displayName": "Programvaresystemer"
    }""")
# PVS-course
"""{
        "type": "fc:fs:emne",
        "parent": "fc:org:ntnu.no",
        "membership": {
            "basic": "member",
            "active": true,
            "fsroles": [
                "STUDENT"
            ],
            "displayName": "Student"
        },
        "id": "fc:fs:fs:emne:ntnu.no:IT3901:1",
        "displayName": "Masteroppgave i informatikk: Programvaresystemer"
    }"""

# Courses

NON_INFORMATICS_COURSE_ACTIVE = json.loads("""{
        "type": "fc:fs:emne",
        "parent": "fc:org:ntnu.no",
        "membership": {
            "basic": "member",
            "notAfter": "%s-12-14T23:00:00Z",
            "fsroles": [
                "STUDENT"
            ],
            "displayName": "Student",
            "subjectRelations": "undervisning",
            "active": true
        },
        "id": "fc:fs:fs:emne:ntnu.no:EXPH0004:1",
        "displayName": "Examen philosophicum for naturvitenskap og teknologi"
    }""")

NON_INFORMATICS_COURSE_EXPIRED = json.loads("""{
        "type": "fc:fs:emne",
        "parent": "fc:org:ntnu.no",
        "membership": {
            "basic": "member",
            "notAfter": "%s-12-14T23:00:00Z",
            "fsroles": [
                "STUDENT"
            ],
            "displayName": "Student",
            "subjectRelations": "undervisning",
            "active": true
        },
        "id": "fc:fs:fs:emne:ntnu.no:EXPH0004:1",
        "displayName": "Examen philosophicum for naturvitenskap og teknologi"
    }""")

ITGK_ACTIVE = json.loads("""{
        "type": "fc:fs:emne",
        "parent": "fc:org:ntnu.no",
        "membership": {
            "basic": "member",
            "notAfter": "%s-12-14T23:00:00Z",
            "fsroles": [
                "STUDENT"
            ],
            "displayName": "Student",
            "subjectRelations": "undervisning",
            "active": true
        },
        "id": "fc:fs:fs:emne:ntnu.no:TDT4110:1",
        "displayName": "Informasjonsteknologi, grunnkurs"
    }""")

ITGK_EXPIRED = json.loads("""{
        "type": "fc:fs:emne",
        "parent": "fc:org:ntnu.no",
        "membership": {
            "basic": "member",
            "notAfter": "%s-12-14T23:00:00Z",
            "fsroles": [
                "STUDENT"
            ],
            "displayName": "Student",
            "subjectRelations": "undervisning",
            "active": true
        },
        "id": "fc:fs:fs:emne:ntnu.no:TDT4110:1",
        "displayName": "Informasjonsteknologi, grunnkurs"
    }""")

WEBTEK_ACTIVE = json.loads("""{
        "type": "fc:fs:emne",
        "parent": "fc:org:ntnu.no",
        "membership": {
            "basic": "member",
            "notAfter": "%s-12-14T23:00:00Z",
            "fsroles": [
                "STUDENT"
            ],
            "displayName": "Student",
            "subjectRelations": "undervisning",
            "active": true
        },
        "id": "fc:fs:fs:emne:ntnu.no:IT2805:1",
        "displayName": "Webteknologi"
    }""")

WEBTEK_EXPIRED = json.loads("""{
        "type": "fc:fs:emne",
        "parent": "fc:org:ntnu.no",
        "membership": {
            "basic": "member",
            "notAfter": "%s-12-14T23:00:00Z",
            "fsroles": [
                "STUDENT"
            ],
            "displayName": "Student",
            "subjectRelations": "undervisning",
            "active": true
        },
        "id": "fc:fs:fs:emne:ntnu.no:IT2805:1",
        "displayName": "Webteknologi"
    }""")

PROJECT1_ACTIVE = json.loads("""{
        "type": "fc:fs:emne",
        "parent": "fc:org:ntnu.no",
        "membership": {
            "basic": "member",
            "notAfter": "%s-12-14T23:00:00Z",
            "fsroles": [
                "STUDENT"
            ],
            "displayName": "Student",
            "subjectRelations": "undervisning",
            "active": true
        },
        "id": "fc:fs:fs:emne:ntnu.no:IT1901:1",
        "displayName": "Informatikk prosjektarbeid I"
    }""")

PROJECT1_EXPIRED = json.loads("""{
        "type": "fc:fs:emne",
        "parent": "fc:org:ntnu.no",
        "membership": {
            "basic": "member",
            "notAfter": "%s-12-14T23:00:00Z",
            "fsroles": [
                "STUDENT"
            ],
            "displayName": "Student",
            "subjectRelations": "undervisning",
            "active": true
        },
        "id": "fc:fs:fs:emne:ntnu.no:IT1901:1",
        "displayName": "Informatikk prosjektarbeid I"
    }""")

PROJECT2_ACTIVE = json.loads("""{
        "type": "fc:fs:emne",
        "parent": "fc:org:ntnu.no",
        "membership": {
            "basic": "member",
            "notAfter": "%s-08-14T22:00:00Z",
            "fsroles": [
                "STUDENT"
            ],
            "displayName": "Student",
            "subjectRelations": "undervisning",
            "active": true
        },
        "id": "fc:fs:fs:emne:ntnu.no:IT2901:1",
        "displayName": "Informatikk prosjektarbeid II"
    }""")

PROJECT2_EXPIRED = json.loads("""{
        "type": "fc:fs:emne",
        "parent": "fc:org:ntnu.no",
        "membership": {
            "basic": "member",
            "notAfter": "%s-08-14T22:00:00Z",
            "fsroles": [
                "STUDENT"
            ],
            "displayName": "Student",
            "subjectRelations": "undervisning",
            "active": true
        },
        "id": "fc:fs:fs:emne:ntnu.no:IT2901:1",
        "displayName": "Informatikk prosjektarbeid II"
    }""")


PVS_ACTIVE = json.loads("""{
        "type": "fc:fs:emne",
        "parent": "fc:org:ntnu.no",
        "membership": {
            "basic": "member",
            "active": true,
            "fsroles": [
                "STUDENT"
            ],
            "displayName": "Student"
        },
        "id": "fc:fs:fs:emne:ntnu.no:IT3901:1",
        "displayName": "Masteroppgave i informatikk: Programvaresystemer"
    }""")

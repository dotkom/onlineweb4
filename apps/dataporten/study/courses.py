# Configuration

GROUP_IDENTIFIERS = {
    # Studies
    # The study programs are identified by the descriptor: `fc:fs:prg`
    'BACHELOR': 'fc:fs:fs:prg:ntnu.no:BIT',
    'MASTER': 'fc:fs:fs:prg:ntnu.no:MIT',
    'IDI': 'fc:org:ntnu.no:unit:631000',

    # fc:fs:fs:str:ntnu.no:MIT-PVS- programvaresys
    # fc:fs:fs:str:ntnu.no:MIT-KI - kunstig int

    # Courses used for verification

    # 1st grade
    'ITGK': 'fc:fs:fs:emne:ntnu.no:TDT4110:1',
    'WEBTEK': 'fc:fs:fs:emne:ntnu.no:IT2805:1',

    # 2nd grade
    'PROSJEKT1': 'fc:fs:fs:emne:ntnu.no:IT1901:1',
    'ALGDAT': 'fc:fs:fs:emne:ntnu.no:TDT4120:1',

    # 3rd grade
    'PROSJEKT2': 'fc:fs:fs:emne:ntnu.no:IT2901:1',

    # Master project courses
    'MASTER_COURSE': 'fc:fs:fs:emne:ntnu.no:IT3901',
    'MASTER_COURSE_PVS': 'fc:fs:fs:emne:ntnu.no:IT3901:1',
    'MASTER_COURSE_DB': 'fc:fs:fs:emne:ntnu.no:IT3902:1',
    'MASTER_COURSE_AI': 'fc:fs:fs:emne:ntnu.no:IT3903:1',
    'MASTER_COURSE_UX': 'fc:fs:fs:emne:ntnu.no:IT3906:1',
    'MASTER_COURSE_OTHER': 'fc:fs:fs:emne:ntnu.no:IT3950:1',
}


def get_courses_for_key(d, key):
    return [course for k, course in d.items() if key in k]


MASTER_IDS = get_courses_for_key(GROUP_IDENTIFIERS, 'MASTER_COURSE_')

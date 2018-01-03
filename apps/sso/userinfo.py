class Onlineweb4Userinfo(object):
    """ Generate userinfo for onlineweb4 claim. """

    def __init__(self, user):
        self.userinfo = {
            'username': user.username,
            'member': user.is_member,
            'staff': user.is_staff,
            'superuser': user.is_superuser,
            'rfid': user.rfid,
            'field_of_study': user.get_field_of_study_display(),
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.get_email().email,
            'nickname': user.nickname,
            'image': user.get_image_url(),
        }

    def oauth2(self):
        return self.userinfo

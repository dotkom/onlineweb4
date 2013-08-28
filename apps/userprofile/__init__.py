from django.contrib.auth.models import User
from apps.userprofile.models import Privacy

User.privacy = property(lambda u: Privacy.objects.get_or_create(user=u)[0])
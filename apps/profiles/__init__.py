from apps.authentication.models import OnlineUser as User
from apps.profiles.models import Privacy

User.privacy = property(lambda u: Privacy.objects.get_or_create(user=u)[0])
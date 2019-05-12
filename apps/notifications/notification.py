from apps.notifications.models import NotificationSetting as Setting, NotificationSubscription as Subscription
from apps.notifications.tasks import send_webpush


class Notification:

    message_type = None

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.args = args
        self.kwargs = kwargs

        if not self.message_type:
            raise ValueError('Notification is missing message_type')

    def dispatch(self):
        """
        Dispatch notification to selected dispatchers by user
        """

        settings: Setting = Setting.get_for_user_by_type(self.user, self.message_type)

        """ Dispatch notification to user if the user has them enabled """

        if settings.push:
            self.dispatch_push()

        """ This form of email notifications have not been implemented yet
        if settings.mail:
            self.dispatch_mail()
        """

    def dispatch_mail(self):
        raise NotImplementedError('This form of email notifications have not been implemented yet')

    def dispatch_push(self):
        device_subscriptions = Subscription.objects.filter(user=self.user)
        data = self.build_push_data()
        for subscription in device_subscriptions:
            send_webpush(subscription=subscription, data=data)

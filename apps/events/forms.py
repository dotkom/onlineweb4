from django import forms
from captcha.fields import CaptchaField

class CaptchaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CaptchaForm, self).__init__(*args, **kwargs)
        # Removing mark rules field if user has already accepted the rules
        if user and user.is_authenticated() and user.mark_rules:
            del self.fields['mark_rules']
    mark_rules = forms.BooleanField(label=u'Jeg godtar <a href="/profile/#marks" target="_blank">prikkreglene</a>')
    captcha = CaptchaField()

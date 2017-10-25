from django import forms


class SetRFIDForm(forms.Form):
    rfid = forms.CharField()

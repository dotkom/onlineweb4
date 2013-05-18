from django import forms

class UploadForm(forms.Form):
    docfile = forms.FileField(label='', required=True, help_text='max. 42. megabytes')
    video_name = forms.CharField(label="Video name=")

def createUploadForm(size):
    upload_form = UploadForm()
    if int(size) > 1024 ** 3:
        size = str(int(size) / 1024 ** 3) + "GB"
    else:
        size  = str(int(size) / 1024 ** 2) + "MB"
        
    upload_form.fields['docfile'].help_text = size + " ledig plass."
    return upload_form

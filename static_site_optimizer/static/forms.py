from django import forms

class UploadForm(forms.Form):
    zip_file = forms.FileField()

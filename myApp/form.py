from django import forms

from myApp.models import user_data, query_login, SingleLineModel, DoubleLineModel


class Form(forms.ModelForm):
    class Meta:
        model=user_data
        fields = ['Name', 'Institution', 'Email', 'Password']

class QueryLoginForm(forms.ModelForm):
    class Meta:
        model=query_login
        fields = ['Email', 'Password']

class SingleLineForm(forms.ModelForm):
    class Meta:
        model=SingleLineModel
        fields = ['Field']

class DoubleLineForm(forms.ModelForm):
    class Meta:
        model=DoubleLineModel
        fields = ['field1', 'field2']


class UploadFileForm(forms.Form):
    Title = forms.CharField(max_length=50)
    CourseTeacher = forms.CharField(max_length=100)
    File = forms.FileField()
    Tag=forms.CharField(max_length=100)


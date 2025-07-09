from django import forms
from . import models


class RegisterForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['mobile', 'password']



class SignUpForm(forms.Form):
    username = forms.CharField(label='username')
    email = forms.CharField(label='email')
    mobile = forms.CharField(label='mobile')
    password = forms.CharField(label='password')
    retyped_password = forms.CharField(label='retyped_password')


class SignInForm(forms.Form):
    username = forms.CharField(label='username')
    password = forms.CharField(label='password')


class IdentityInformationForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    race = forms.CharField(max_length=100, required=True)
    type = forms.CharField(max_length=100, required=True)
    dob = forms.CharField(label='dob', required=True)
    image = forms.ImageField(required=True)




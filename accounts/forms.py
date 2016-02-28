from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import TextInput, PasswordInput, CheckboxInput

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_developer = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None


    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email','is_developer')
        """widgets = {
            'username': TextInput(attrs={'class': 'form-control w3-border'}),
            'password1': PasswordInput(attrs={'class': 'form-control w3-border'}),
            'password2': PasswordInput(attrs={'class': 'form-control w3-border'}),
            'is_developer': CheckboxInput(attrs={'class': 'form-control w3-border'}),
        }"""

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.is_developer = self.cleaned_data["is_developer"]
        user.email = self.cleaned_data["email"]
        user.save()

        if commit:
            user.is_active = False # not active until he opens activation link
            user.save()
        return user
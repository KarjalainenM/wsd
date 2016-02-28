from django.forms import ModelForm
from django import forms
from .models import Game


class GameForm(ModelForm):
    
    class Meta:
        model = Game
        fields = ['name', 'price', 'URL', 'categories', 'description', 'image', 'developer']
        widgets = {'developer': forms.HiddenInput()}

class PaymentForm(forms.Form):
    pid = forms.IntegerField(widget=forms.HiddenInput)
    sid = forms.CharField(widget=forms.HiddenInput)
    success_url = forms.URLField(widget=forms.HiddenInput)
    cancel_url = forms.URLField(widget=forms.HiddenInput)
    error_url = forms.URLField(widget=forms.HiddenInput)
    amount = forms.IntegerField(widget=forms.HiddenInput)
    checksum = forms.CharField(widget=forms.HiddenInput)

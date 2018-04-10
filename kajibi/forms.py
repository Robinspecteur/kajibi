from django.forms import ModelForm, TextInput, EmailInput, DateInput, Textarea
from .models import Location, Game
from django import forms
from dal import autocomplete
import datetime


class BootstrapModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BootstrapModelForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })


class LocationForm(BootstrapModelForm):
    class Meta:
        model = Location
        fields = ['renter_first_name', 'renter_last_name', 'renter_address', 'renter_phone', 'renter_email',
                  'renter_guarantee', 'renter_group', 'rented_games', 'expected_date_end', 'comments', 'rented_games']
        widgets = {
            'renter_first_name': TextInput(attrs={'placeholder': 'Prénom'}),
            'renter_last_name': TextInput(attrs={'placeholder': 'Nom'}),
            'renter_address': TextInput(attrs={'placeholder': '123 rue lambda'}),
            'renter_phone': TextInput(attrs={'placeholder': '0123456789'}),
            'renter_email': EmailInput(attrs={'placeholder': 'abc@xyz.com'}),
            'renter_group': TextInput(attrs={'placeholder': 'KAP, Cercle, Régio, ...'}),
            'expected_date_end': DateInput(attrs={'placeholder': '1 janvier 2020'}),
            'rented_games': autocomplete.ModelSelect2Multiple(url='game_autocomplete'),
            'comments': Textarea(attrs={'rows': 5})
        }

    def clean_expected_date_end(self):
        expected_date_end = self.cleaned_data['expected_date_end']
        if expected_date_end < datetime.date.today():
            raise forms.ValidationError("Veuillez saisir une date valide")
        else:
            return expected_date_end


class BootstrapLoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BootstrapLoginForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })


class LoginForm(BootstrapLoginForm):
    username = forms.CharField(label="Nom d'utilisateur", max_length=30, widget=forms.TextInput(
        attrs={'placeholder': 'Kajien'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}))


class SearchForm(forms.Form):
    query = forms.CharField(label="Recherche", max_length=50)



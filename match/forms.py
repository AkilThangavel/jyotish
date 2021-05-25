from django import forms
from .models import User


class PersonAddForm(forms.Form):
    inputNameAdd = forms.CharField(max_length=32)
    inputDateAdd = forms.CharField(max_length=10)
    inputTimeAdd = forms.CharField(max_length=5)
    autocomplete2 = forms.CharField(max_length=200)
    inputGenderAdd = forms.CharField(max_length=6)

class PersonEditForm(forms.Form):
    inputNameEdit = forms.CharField(max_length=32)
    inputDateEdit = forms.CharField(max_length=10)
    inputTimeEdit = forms.CharField(max_length=5)
    autocomplete1 = forms.CharField(max_length=200)
    inputGenderEdit = forms.CharField(max_length=6)
    nameEditHidden = forms.CharField(max_length=32)
    bdateEditHidden = forms.CharField(max_length=10)
    btimeEditHidden = forms.CharField(max_length=5)
    bplaceEditHidden = forms.CharField(max_length=200)
    genderEditHidden = forms.CharField(max_length=6)

class PersonMatchForm(forms.Form):
    inputPerson1 = forms.CharField(max_length=300)
    inputPerson2 = forms.CharField(max_length=300)

# Form for signing in
class SignInForm(forms.Form):
    class Meta:
        model = User
        fields = ('username', 'password')
        widgets = {
            'password': forms.PasswordInput()
        }
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)

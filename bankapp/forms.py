from django import forms

class TransactionPinForm(forms.Form):
    pin = forms.IntegerField(widget=forms.PasswordInput)
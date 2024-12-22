from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import FinDataA, Company, AnalystUser

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'ticker', 'currency', 'country', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'ticker': forms.TextInput(attrs={'class': 'form-control'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'price_updated': forms.TextInput(attrs={'readonly': 'readonly'}), 
            'price': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price can not be negative.")
        return price

class FinDataForm(forms.ModelForm):
    class Meta:
        model = FinDataA
        fields = [field.name for field in FinDataA._meta.fields if field.name != 'company']
        
class RegistrationForm(UserCreationForm):
    class Meta:
        model = AnalystUser
        fields = ['username', 'email', 'password1', 'password2']

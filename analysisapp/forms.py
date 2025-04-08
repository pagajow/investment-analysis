from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse
from .models import FinReport, AssetNote, FinDataA, Company, AnalystUser, AssetFilter
from django.contrib.auth.hashers import check_password
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.utils.safestring import mark_safe


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['favorite', 'name', 'ticker', 'description', 'is_company', 'currency', 'country', 'price',]
        widgets = {
            'favorite': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_company': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'ticker': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'is_company': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
    
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Username"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password"
    )
class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '',
            'autocomplete': 'email'
        })
class CustomPasswordResetConfirmForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        })
        
class RegistrationForm(UserCreationForm):
    accept_terms = forms.BooleanField(
        required=True
    )

    
    class Meta:
        model = AnalystUser
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': 'required'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
        
        self.fields['accept_terms'].widget.attrs.update({'class': 'form-check-input'})
        terms_url = reverse('terms_of_service')
        privacy_url = reverse('privacy_policy')
        self.fields['accept_terms'].label = mark_safe(
            f'I accept the <a href="{terms_url}" target="_blank">Terms of Service</a> '
            f'and <a href="{privacy_url}" target="_blank">Privacy Policy</a>:'
        )
        self.fields['accept_terms'].widget = forms.CheckboxInput(attrs={'class': 'form-check-input'})

    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if AnalystUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Ten adres email jest już zajęty.")
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = AnalystUser
        fields = ['username', 'email', 'first_name', 'last_name', 'openai_api_key', 'google_api_key', 'google_cse_id', 'date_joined', 'last_login']
        exclude = ["password"]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'openai_api_key': forms.TextInput(attrs={'class': 'form-control'}),
            'google_api_key': forms.TextInput(attrs={'class': 'form-control'}),
            'google_cse_id': forms.TextInput(attrs={'class': 'form-control'}),
            'date_joined': forms.DateTimeInput(attrs={'readonly': 'readonly', 'class': 'form-control'}), 
            'last_login': forms.DateTimeInput(attrs={'readonly': 'readonly', 'class': 'form-control'}), 
        }
        
    def __init__(self, *args, **kwargs): 
        super(ProfileForm, self).__init__(*args, **kwargs) 
        self.fields['username'].help_text = ""
        self.fields['date_joined'].disabled = True 
        self.fields['last_login'].disabled = True


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'  # Dodanie klasy Bootstrap
    
class AssetNoteForm(forms.ModelForm):
    class Meta:
        model = AssetNote
        fields = ['favorite', 'title', 'content', ] 
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'favorite': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class FinReportForm(forms.ModelForm):
    class Meta:
        model = FinReport
        fields = ['favorite', 'title', 'content', ] 
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'favorite': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
class AssetFilterForm(forms.ModelForm):
    class Meta:
        model = AssetFilter
        fields = ["function", "data", "periods", "check_type", "value1", "value2", "weight"]
        widgets = {
            "data": forms.Select(attrs={'class': 'form-control'}),
            "function": forms.Select(attrs={'class': 'form-control'}),
            "periods": forms.NumberInput(attrs={'class': 'form-control', "step": 1, "min": 1, "max": 10}),  
            "check_type": forms.Select(attrs={'class': 'form-control', "id": "id_check_type"}),
            "value1": forms.NumberInput(attrs={'class': 'form-control', "step": "any", "id": "id_value1"}),
            "value2": forms.NumberInput(attrs={'class': 'form-control', "step": "any", "id": "id_value2"}),
            "weight": forms.NumberInput(attrs={'class': 'form-control', "step": 1, "min": 1}),  
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamiczne ustawianie etykiet
        self.fields["value1"].label = "Threshold Value"
        self.fields["value2"].label = "Second Threshold Value"

        # Usunięcie pustej opcji w check_type
        self.fields["check_type"].choices = [
            choice for choice in self.fields["check_type"].choices if choice[0] != ""
        ]

    def clean(self):
        cleaned_data = super().clean()
        check_type = cleaned_data.get("check_type")
        value1 = cleaned_data.get("value1")
        value2 = cleaned_data.get("value2")

        if check_type in ["range", "beyond"] and value1 is not None and value2 is not None:
            if value1 > value2:
                self.add_error("value1", "Value1 must be greater than Value2 for 'range' or 'beyond'.")

        return cleaned_data
    
    
    
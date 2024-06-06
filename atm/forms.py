from django import forms
from django.contrib.auth.models import User
from .models import City


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return confirm_password
    
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class DepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=15, decimal_places=2, label='存款金額')

class WithdrawForm(forms.Form):
    amount = forms.DecimalField(max_digits=15, decimal_places=2, label='取款金額')

class TransferForm(forms.Form):
    destination_account_number = forms.CharField(label='目標帳戶', initial='000-001')
    amount = forms.DecimalField(max_digits=15, decimal_places=2, label='轉帳金額')

class PaymentForm(forms.Form):
    amount = forms.DecimalField(max_digits=15, decimal_places=2, label='支付金額')

class FilterForm(forms.Form):
    YES_NO_CHOICES = (
        ('', 'Select'),
        ('y', 'Yes'),
        ('n', 'No'),
    )
    city_town = forms.ModelChoiceField(queryset=City.objects.all(), empty_label="Select City/Town", required=False,label="縣市")
    service_time = forms.TimeField(input_formats=['%H:%M'], help_text="Format: 00:00",required=False,label="期望時間")
    use_wheel = forms.ChoiceField(choices=YES_NO_CHOICES, required=False,label="支援輪椅")
    voice = forms.ChoiceField(choices=YES_NO_CHOICES, required=False,label="支援聽障")
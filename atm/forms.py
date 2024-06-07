from django import forms
from django.contrib.auth.models import User
from .models import City
from captcha.fields import CaptchaField


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
    username = forms.CharField(
        label='用户名',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '输入用户名'
        })
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '输入密码'
        })
    )
    captcha = CaptchaField(label='验证码')

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
        ("", 'Select'),
        ('y', 'Yes'),
        ('n', 'No'),
    )
    TIME_CHOICES=[
        ("", 'Select'),
    ]
    for i in range(0,25):
        hour=str(i).zfill(2)
        TIME_CHOICES.append((hour+":00:00",hour+":00"))
    
    city_town = forms.ModelChoiceField(
        queryset=City.objects.all(),
        empty_label="Select City/Town",
        required=False,
        label="縣市",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    service_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        required=False,
        label="期望時間",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    use_wheel = forms.ChoiceField(
        choices=YES_NO_CHOICES,
        required=False,
        label="支援輪椅",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    voice = forms.ChoiceField(
        choices=YES_NO_CHOICES,
        required=False,
        label="支援聽障",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    captcha = CaptchaField()
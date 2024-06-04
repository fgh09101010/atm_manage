from django import forms
from django.contrib.auth.models import User

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
    amount = forms.DecimalField(max_digits=15, decimal_places=2, label='存款金额')

class WithdrawForm(forms.Form):
    amount = forms.DecimalField(max_digits=15, decimal_places=2, label='取款金额')

class TransferForm(forms.Form):
    destination_account_number = forms.CharField(label='目标账户号码', initial='000-001')
    amount = forms.DecimalField(max_digits=15, decimal_places=2, label='转账金额')

class PaymentForm(forms.Form):
    amount = forms.DecimalField(max_digits=15, decimal_places=2, label='支付金额')

from django import forms
from django.forms import DateInput
from .models import Employee, Leave

class LoginForm(forms.Form):
    phone = forms.CharField(max_length=10, label='Phone Number')
    pin = forms.CharField(max_length=4, widget=forms.PasswordInput, label='4 digit pin')

class ChangePinForm(forms.Form):
    current_pin = forms.CharField(max_length=4, required=True, widget=forms.PasswordInput, label='Current Pin')
    new_pin = forms.CharField(max_length=4, required=True, widget=forms.PasswordInput, label='New Pin')
    confirm_pin = forms.CharField(max_length=4, required=True, widget=forms.PasswordInput, label='Confirm Pin')

    def clean(self):
        cleaned_data = super().clean()
        new_pin = cleaned_data.get('new_pin')
        confirm_pin = cleaned_data.get('confirm_pin')

        if new_pin != confirm_pin:
            raise forms.ValidationError('New Pin & Confirm Pin do not match')
        return cleaned_data


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'phone', 'status', 
            'role', 'total_cs_leave', 'total_e_leave'
        ]
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError('Phone number must be exactly 10 digits.')
        return phone

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': DateInput(attrs={'type':'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
        }

    
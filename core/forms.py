from django import forms
from .models import Announcement, LeaveRequest, Employee, Payroll
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class LeaveForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'reason']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['department', 'designation', 'join_date', 'phone', 'address']

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='First Name')
    last_name = forms.CharField(max_length=30, required=True, label='Last Name')
    email = forms.EmailField(required=True)
    department = forms.CharField(max_length=100)
    designation = forms.CharField(max_length=100)
    join_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    phone = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)
    is_hr = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2',
            'department', 'designation', 'join_date', 'phone', 'address', 'is_hr'
        ]

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'message']

class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['employee', 'month', 'salary', 'bonus', 'deductions']
        widgets = {
            'month': forms.DateInput(attrs={'type': 'month', 'class': 'form-control'}),
        }
# dashboard/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
# dashboard/forms.py
from django import forms
from django.utils import timezone
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if start_time < timezone.now():
                raise forms.ValidationError("Cannot reserve seats in the past")
            if end_time <= start_time:
                raise forms.ValidationError("End time must be after start time")
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': 'At least 8 characters'
        }),
        min_length=8
    )
    
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'role', 'filiere', 'year', 'password']
        widgets = {
            'role': forms.RadioSelect(),
            'filiere': forms.Select(choices=[
                ('', 'Select your filière'),
                ('GI', 'Genie Informatique'),
                ('GM', 'Genie Mecanique'),
                ('GP', 'Genie Physique'),
            ]),
            'year': forms.Select(choices=CustomUser.YEAR_CHOICES),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'placeholder': 'John'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Doe'})
        self.fields['email'].widget.attrs.update({'placeholder': 'john.doe@ensam-casa.ma'})

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        if role == 'student':
            if not cleaned_data.get('filiere'):
                self.add_error('filiere', 'Filière is required for students')
            if not cleaned_data.get('year'):
                self.add_error('year', 'Academic year is required for students')
        else:
            if cleaned_data.get('filiere'):
                self.add_error('filiere', 'Filière should only be set for students')
            if cleaned_data.get('year'):
                self.add_error('year', 'Academic year should only be set for students')
        
        return cleaned_data
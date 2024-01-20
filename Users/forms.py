from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.forms import CharField, EmailField, Form, ModelForm, PasswordInput

from .models import Profile


class ProfileForm(ModelForm):
    email = EmailField(required=True)

    class Meta:
        model = Profile
        fields = ['profile_image', 'city', 'street', 'house_number', 'postal_code', 'phone_number', 'gender']
        labels = {
            'profile_image': 'Zdjęcie profilowe',
            'city': 'Miasto',
            'street': 'Ulica',
            'house_number': 'Numer domu/mieszkania',
            'postal_code': 'Kod pocztowy',
            'phone_number': 'Numer telefonu',
            'gender': 'Płeć',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['email'].initial = self.instance.user.email

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input'})

    def save(self, commit=True):
        profile = super(ProfileForm, self).save(commit=False)
        profile.user.email = self.cleaned_data['email'].lower()
        if commit:
            profile.save()
            profile.user.save()
        return profile


class ChangePasswordForm(Form):
    old_password = CharField(
        label="Aktualne hasło",
        widget=PasswordInput(attrs={'autocomplete': 'current-password'}))

    new_password1 = CharField(
        label="Nowe hasło",
        widget=PasswordInput(attrs={'autocomplete': 'new-password'}),
        validators=[validate_password]
    )
    new_password2 = CharField(
        label="Potwierdź nowe hasło",
        widget=PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input'})

    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user

from django import forms
from django.contrib.auth import password_validation

from user.models import User


class UserCreationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': 'Zadané heslá sa nezhodujú'
    }
    new_password1 = forms.CharField(
        label='Heslo',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label='Potvrdenie hesla',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text='Zadaj to isté heslo ešte raz pre potvrdenie',
    )

    class Meta:
        model = User
        fields = ['email', 'new_password1',
                  'new_password2', 'first_name', 'last_name', ]

    def __init__(self, *args, **kwargs):
        # pylint: disable=no-member
        super(UserCreationForm, self).__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs['autofocus'] = True

    def clean_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch')
        return password2

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get('new_password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error('new_password2', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['new_password1'])
        if commit:
            user.save()
        return user


class NameUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', ]

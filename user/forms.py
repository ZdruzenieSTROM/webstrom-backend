from django import forms
from django.contrib.auth.password_validation import validate_password

from competition.models import Grade
from user.models import County, District, Profile, User


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

    password1 = forms.CharField(label='Heslo', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Potvrdenie hesla', widget=forms.PasswordInput)

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        validate_password(password1)
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Heslá sa nezhodujú')
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()

        return user


class ProfileCreationForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'nickname',
                  'county', 'district', 'school', 'school_info',
                  'grade', 'phone', 'parent_phone', 'gdpr',)

    grade = forms.ModelChoiceField(
        queryset=Grade.objects.filter(is_active=True), label='Ročník')
    school_info = forms.CharField(
        widget=forms.Textarea, required=False,
        label='povedz nám, kam chodíš na školu, aby sme ti ju mohli dodatočne pridať')

    county = forms.ModelChoiceField(queryset=County.objects, label='Kraj')
    district = forms.ModelChoiceField(queryset=District.objects, label='Okres')

    def __init__(self, *args, **kwargs):
        super(ProfileCreationForm, self).__init__(*args, **kwargs)

        self.fields['county'].queryset = County.objects.all_except_unspecified()

    def clean_gdpr(self):
        gdpr = self.cleaned_data['gdpr']

        if not gdpr:
            raise forms.ValidationError(
                'Súhlas so spracovaním osobných údajov je nutnou podmienkou registrácie')

        return gdpr

    def save(self, commit=True):
        profile = super(ProfileCreationForm, self).save(commit=False)

        profile.year_of_graduation = \
            self.cleaned_data['grade'].get_year_of_graduation_by_date()

        if commit:
            profile.save()

        return profile

from datetime import date

from django import forms
from django.db.models import IntegerChoices

from user.models import County, District, Profile, School, User


class GradeChoices(IntegerChoices):
    # TODO: toto sa ešte môže zísť inde, prehodiť to niekam inam
    Z1 = 12, 'Prvý ročník ZŠ'
    Z2 = 11, 'Druhý ročník ZŠ'
    Z3 = 10, 'Tretí ročník ZŠ'
    Z4 = 9, 'Štvrtý ročník ZŠ'
    Z5 = 8, 'Piaty ročník ZŠ'
    Z6 = 7, 'Šiesty ročník ZŠ | Príma'
    Z7 = 6, 'Siedmy ročník ZŠ | Sekunda'
    Z8 = 5, 'Ôsmy ročník ZŠ | Tercia'
    Z9 = 4, 'Deviaty ročník ZŠ | Kvarta'
    S1 = 3, 'Prvý ročník SŠ | Kvinta'
    S2 = 2, 'Druhý ročník SŠ | Sexta'
    S3 = 1, 'Tretí ročník SŠ | Septima'
    S4 = 0, 'Štvrtý ročník SŠ | Oktáva'
    XX = -1, 'Už nechodím do školy'


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

    password1 = forms.CharField(label='Heslo', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Potvrdenie hesla', widget=forms.PasswordInput)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Heslá sa nezhodujú')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class ProfileCreationForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'nickname',
                  'county', 'district', 'school', 'school_info',
                  'grade', 'phone', 'parent_phone')

    grade = forms.ChoiceField(
        choices=GradeChoices.choices, required=True, label='ročník')
    school_info = forms.CharField(
        widget=forms.Textarea, required=False,
        label='povedz nám, kam chodíš na školu, aby sme ti ju mohli dodatočne pridať')

    county = forms.ModelChoiceField(queryset=County.objects, label='kraj')
    district = forms.ModelChoiceField(queryset=District.objects, label='okres')

    def __init__(self, *args, **kwargs):
        super(ProfileCreationForm, self).__init__(*args, **kwargs)

        self.fields['district'].queryset = District.objects.none()
        self.fields['school'].queryset = School.objects.none()

    def save(self, commit=True):
        profile = super(ProfileCreationForm, self).save(commit=False)

        # TODO: toto sa ešte hodí inde, vybrať niekde von
        today = date.today()
        s4_graduation_year = today.year

        if today >= date(today.year, 9, 1):
            s4_graduation_year += 1

        profile.year_of_graduation = s4_graduation_year + \
            int(self.cleaned_data['grade'])

        if commit:
            profile.save()

        return profile

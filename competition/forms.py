from django import forms
from django.core.mail import mail_managers
from django.template.loader import render_to_string
from profile.models import County, District, Profile, School
from competition.models import Grade


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nickname',
                  'school_not', 'county', 'district', 'school',
                  'school_name', 'school_not_found', 'school_info',
                  'grade', 'phone', 'parent_phone', 'gdpr', ]

    grade = forms.ModelChoiceField(
        queryset=Grade.objects.filter(is_active=True),
        label='Ročník',
        help_text='V prípade, že je leto, zadaj ročník, '
        'ktorý končíš (školský rok začína septembrom).')

    school_not = forms.BooleanField(
        required=False,
        label='Už nie som študent základnej ani strednej školy.')

    school_name = forms.CharField(
        required=False,
        label='Škola*')

    school_not_found = forms.BooleanField(
        required=False,
        label='Moja škola sa v zozname nenachádza.')

    school_info = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label='povedz nám, kam chodíš na školu, aby sme ti ju mohli dodatočne pridať')

    county = forms.ModelChoiceField(
        required=False,
        queryset=County.objects,
        label='Kraj školy')

    district = forms.ModelChoiceField(
        required=False,
        queryset=District.objects,
        label='Okres školy')

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        self.fields['county'].queryset = County.objects.all_except_unspecified()
        self.fields['school'].widget = forms.HiddenInput()

    def clean_gdpr(self):
        gdpr = self.cleaned_data['gdpr']

        if not gdpr:
            raise forms.ValidationError(
                'Súhlas so spracovaním osobných údajov je nutnou podmienkou registrácie')

        return gdpr

    def clean_school_info(self):
        school = self.cleaned_data['school']
        school_info = self.cleaned_data['school_info']

        if school == School.objects.get_unspecified_value() and not school_info:
            raise forms.ValidationError(
                'Ak si nenašiel svoju školu, napíš nám na akú školu chodíš')

        return school_info


class ProfileCreationForm(ProfileForm):
    class Meta:
        model = Profile
        fields = ['nickname',
                  'school_not', 'county', 'district', 'school',
                  'school_name', 'school_not_found', 'school_info',
                  'grade', 'phone', 'parent_phone', 'gdpr', ]

    def save(self, user, commit=True):
        # pylint: disable=arguments-differ
        profile = super(ProfileCreationForm, self).save(commit=False)
        profile.user = user

        profile.year_of_graduation = \
            self.cleaned_data['grade'].get_year_of_graduation_by_date()

        school_county = self.cleaned_data['county']
        school_info = self.cleaned_data['school_info']

        if self.cleaned_data['school_info']:
            mail_managers(
                'Požiadavka na pridanie školy do databázy',
                render_to_string(
                    'competition/emails/new_school_request.txt',
                    {'user': profile.user, 'school': school_info,
                     'school_county': school_county})
            )

        if commit:
            profile.save()

        return profile


class ProfileUpdateForm(ProfileForm):
    class Meta:
        model = Profile
        fields = ['nickname',
                  'school_not', 'county', 'district', 'school',
                  'school_name', 'school_not_found', 'school_info',
                  'grade', 'phone', 'parent_phone', ]


class SeriesSolutionForm(forms.Form):
    def __init__(self, series, *args, **kwargs):
        super(SeriesSolutionForm, self).__init__(*args, **kwargs)

        for problem in series.problems.all():
            self.fields[str(problem.pk)] = forms.FileField(
                label='Tvoje riešenie',
                required=False)

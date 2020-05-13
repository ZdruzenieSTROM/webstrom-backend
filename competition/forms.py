from django import forms

from competition.models import County, District, Grade, Profile


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

    def save(self, commit=True):
        profile = super(ProfileForm, self).save(commit=False)

        profile.year_of_graduation = \
            self.cleaned_data['grade'].get_year_of_graduation_by_date()

        if commit:
            profile.save()

        return profile


class ProfileCreationForm(ProfileForm):
    class Meta:
        model = Profile
        fields = ['nickname',
                  'school_not', 'county', 'district', 'school',
                  'school_name', 'school_not_found', 'school_info',
                  'grade', 'phone', 'parent_phone', 'gdpr', ]


class ProfileUpdateForm(ProfileForm):
    class Meta:
        model = Profile
        fields = ['nickname',
                  'school_not', 'county', 'district', 'school',
                  'school_name', 'school_not_found', 'school_info',
                  'grade', 'phone', 'parent_phone', ]

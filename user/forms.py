from django.contrib.auth.forms import \
    UserCreationForm as DefaultUserCreationForm


class UserCreationForm(DefaultUserCreationForm):
    class Meta(DefaultUserCreationForm.Meta):
        fields = ['first_name', 'last_name',
                  'email', 'password1', 'password2', ]

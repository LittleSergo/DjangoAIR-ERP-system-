from django import forms

from .models import User


class SignupForm(forms.ModelForm):
    """Signup form."""
    password = forms.CharField(
        max_length=100, widget=forms.PasswordInput
    )
    confirm_password = forms.CharField(
        max_length=100, widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'password',
            'confirm_password', 'email'
        ]

    def clean(self):
        """Check, is passwords match or not."""
        super(SignupForm, self).clean()

        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password != confirm_password:
            self._errors['password'] = self.error_class([
                'Passwords do not match!'
            ])

        return self.cleaned_data

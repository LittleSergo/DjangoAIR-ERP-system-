from django import forms


class ResetPasswordForm(forms.Form):
    """Form for password reset."""
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=100,
                                       widget=forms.PasswordInput)

    def clean(self):
        """Checking for same airports in the form."""
        super(ResetPasswordForm, self).clean()

        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password != confirm_password:
            self._errors['password'] = self.error_class([
                'Passwords must match.'
            ])

        return self.cleaned_data

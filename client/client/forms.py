from django import forms

from common_instances.models import Ticket, Passenger, Seat, Option, Airport, SeatType, Discount
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


class OnlineCheckIn(forms.ModelForm):
    """Form for online check in."""
    passenger = forms.ModelChoiceField(queryset=Passenger.objects.all(),
                                       disabled=True)
    seat = forms.ModelChoiceField(queryset=Seat.objects.all(),
                                  disabled=True)
    options = forms.ModelMultipleChoiceField(
        queryset=Option.objects.all(), disabled=True)

    class Meta:
        model = Ticket
        fields = ['passenger', 'seat', 'options', ]


CheckInFormSet = forms.modelformset_factory(
    Ticket, OnlineCheckIn, extra=0
)


class SearchForFlightsForm(forms.Form):
    """Form for searching flights by arriving and destination places."""
    arriving = forms.ModelChoiceField(queryset=Airport.objects.all(),
                                      label='From:')
    destination = forms.ModelChoiceField(queryset=Airport.objects.all(),
                                         label='To:')
    date = forms.DateField(widget=forms.SelectDateWidget())
    passengers = forms.IntegerField()

    def clean(self):
        """Checking for same airports in the form."""
        super(SearchForFlightsForm, self).clean()

        arriving = self.cleaned_data.get('arriving')
        destination = self.cleaned_data.get('destination')

        if arriving == destination:
            self._errors['destination_airport'] = self.error_class([
                'Airports should not be the same!'
            ])

        return self.cleaned_data


class BuyTicketForm(forms.ModelForm):
    """Form for buying ticket process."""
    seat_class = forms.ModelChoiceField(SeatType.objects.all(),
                                        label='Class:')
    options = forms.ModelMultipleChoiceField(
        Option.objects.all(),
        required=False,
    )
    promo_code = forms.CharField(max_length=20, required=False)

    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'passport_number',
                  'seat_class', 'options', 'promo_code']

    def clean(self):
        """Checking for same airports in the form."""
        super(BuyTicketForm, self).clean()

        promo_code = self.cleaned_data.get('promo_code')

        if promo_code:
            discount = Discount.objects.filter(promo_code=promo_code)
            if not discount.exists():
                self._errors['promo_code'] = self.error_class([
                    'Wrong promo code.'
                ])

        return self.cleaned_data


def build_formset_with_definite_forms(extra_forms):
    return forms.formset_factory(BuyTicketForm, extra=extra_forms)

from django import forms

from common_instances.models import (
    Flight, User, Option, Ticket, Discount
)
from .models import Pilot


class CreateFlight(forms.ModelForm):
    """Form for flight creation page."""
    pilots = forms.ModelMultipleChoiceField(
        queryset=Pilot.objects.all(),
    )

    class Meta:
        model = Flight
        fields = [
            'number', 'ticket_price', 'boarding_time', 'departure_time',
            'arrival_time', 'distance', 'airplane', 'pilots',
            'departure_airport', 'destination_airport', 'created_by'
        ]

    def clean(self):
        """Checking for same airports in the form."""
        super(CreateFlight, self).clean()

        departure_airport = self.cleaned_data.get('departure_airport')
        destination_airport = self.cleaned_data.get('destination_airport')

        if departure_airport == destination_airport:
            self._errors['destination_airport'] = self.error_class([
                'Airports should not be the same!'
            ])

        return self.cleaned_data


class CreatePilot(forms.ModelForm):
    """Form for pilot creation page."""
    class Meta:
        model = Pilot
        fields = ['first_name', 'last_name', 'category', 'email']


class CreateManager(forms.ModelForm):
    """Form for manager creation page."""
    ROLES = [
        ('gate_manager', 'Gate manager'),
        ('check_in_manager', 'Check-in manager'),
    ]
    role = forms.ChoiceField(choices=ROLES)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'role']


class CreatePlane(forms.Form):
    """Form for plane creation page."""
    number = forms.CharField(max_length=100)
    economy_seat_rows = forms.IntegerField()
    economy_seats_in_row = forms.IntegerField()
    business_seat_rows = forms.IntegerField()
    business_seats_in_row = forms.IntegerField()


class CreateOption(forms.ModelForm):
    """Form for Option creation page."""
    class Meta:
        model = Option
        fields = '__all__'


class CreateDiscount(forms.ModelForm):
    """Form for Discount creation page."""
    class Meta:
        model = Discount
        fields = '__all__'


class CheckInForm(forms.ModelForm):
    """Form for check-in passengers."""
    class Meta:
        model = Ticket
        fields = ['options', ]

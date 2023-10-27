from django.test import TestCase

from ..models import Pilot, User


class ModelsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')

        pilots = [
            ('Tom', 'Cruise', 'tomcruise@gmail.com'),
            ('Tom', 'Hanks', 'tomhanks@gmail.com')
        ]
        self.pilots = [
            Pilot.objects.create(
                first_name=pilot[0],
                last_name=pilot[1],
                category='ATP',
                email=pilot[2]
            ) for pilot in pilots
        ]

    def test_user_model(self):
        """Get created User object and check data."""
        user = User.objects.get(username='testuser')
        self.assertEquals(user.role, 'customer')

    def test_pilot_model(self):
        """Get created pilot object and check."""
        pilot = Pilot.objects.get(last_name='Hanks')
        self.assertEquals(pilot.email, 'tomhanks@gmail.com')

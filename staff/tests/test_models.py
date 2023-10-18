from django.test import TestCase

from ..models import Pilot


class ModelsTests(TestCase):
    def setUp(self):
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

    def test_pilot_model(self):
        """Get created pilot object and check."""
        pilot = Pilot.objects.get(last_name='Hanks')
        self.assertEquals(pilot.email, 'tomhanks@gmail.com')

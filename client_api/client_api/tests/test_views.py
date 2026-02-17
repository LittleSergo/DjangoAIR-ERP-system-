from django.test import TestCase
from django.db import transaction

from datetime import datetime, timedelta
from pytz import timezone

from ..models import User, Purchase
from common_instances.models import (
    Ticket, Airport, Airplane, SeatType, Flight, Seat
)


class TestUserRegistrationView(TestCase):
    def test_register_user_view(self):
        response = self.client.post('/api/v1/users/signup/', data={
            "username": "testuser",
            "email": "test@email.com",
            "password": "testpassword",
            'first_name': 'John',
            'last_name': 'Doe'
        })

        self.assertEquals(response.json()['username'], 'testuser')
        user = User.objects.get(username='testuser')
        self.assertEquals(user.email, "test@email.com")


class TestUserProfileView(TestCase):
    def test_user_profile_get_unauthorized(self):
        response = self.client.get('/api/v1/users/profile/')
        self.assertEquals(response.json(), {
            'detail': 'Authentication credentials were not provided.'
        })

    def test_user_profile_get_authorized(self):
        User.objects.create_user(
            username='testuser',
            password='testpass1234',
            email='test@email.com'
        )
        access_token = self.client.post('/api/v1/token/', data={
            'username': 'testuser',
            'password': 'testpass1234'
        }).json()['access']
        response = self.client.get(
            '/api/v1/users/profile/',
            headers={'Authorization': 'Bearer ' + access_token}
        )
        self.assertEquals(
            response.json()['username'], 'testuser'
        )


class TestPurchasedTicketsView(TestCase):
    def setUp(self):
        self.user = dict(username='testuser', password='testpassword',
                         email='test@gmail.com', email_is_verified=True)
        self.plane = dict(number='testplane')
        self.airports = [('Borispil', 'KBP'), ('Zhuliany', 'IEV')]
        self.flight = dict(
            number='testflight',
            ticket_price=50,
            boarding_time=datetime.now(tz=timezone('EET')),
            departure_time=datetime.now(
                tz=timezone('EET')) + timedelta(hours=2),
            arrival_time=datetime.now(tz=timezone('EET')),
            distance=200,
        )
        self.seat_type = dict(seat_type='Economy', price_multiplier=1)
        self.seat = dict(number='11')
        self.ticket = dict(ticket_code='testticket')
        self.fill_db()
        self.access_token = self.client.post('/api/v1/token/', data={
            'username': 'testuser',
            'password': 'testpassword'
        }).json()['access']

    def fill_db(self):
        self.user = User.objects.create_user(**self.user)
        self.purchase = Purchase.objects.create(user=self.user)
        plane = Airplane.objects.create(
            number='testplane'
        )
        airports = [
            Airport.objects.create(
                name=airport[0],
                city='Kyiv',
                country='Ukraine',
                IATA_code=airport[1]
            ) for airport in self.airports
        ]
        self.flight = Flight.objects.create(
            airplane=plane,
            departure_airport=airports[0],
            destination_airport=airports[1],
            **self.flight
        )
        seat_type = SeatType.objects.create(**self.seat_type)
        seat = Seat.objects.create(airplane=plane, seat_type=seat_type,
                                   **self.seat)
        self.ticket = Ticket.objects.create(seat=seat, flight=self.flight,
                                            **self.ticket)
        self.purchase.tickets.add(self.ticket)
        self.purchase.save()

    def test_purchased_tickets_get(self):
        response = self.client.get(
            '/api/v1/tickets/',
            headers={'Authorization': 'Bearer ' + self.access_token}
        )
        self.assertEquals(
            response.json()[0]['ticket_code'], 'testticket'
        )

    def test_purchased_tickets_retrieve(self):
        response = self.client.get(
            f'/api/v1/tickets/{self.ticket.id}/',
            headers={'Authorization': 'Bearer ' + self.access_token}
        )
        self.assertEquals(
            response.json()['ticket_code'], 'testticket'
        )

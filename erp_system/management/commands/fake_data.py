from datetime import datetime

import faker

from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import (
    User, Flight, Pilot, Airport, Purchase, Passenger, Ticket, Seat,
    Airplane, Option, Discount, SeatType
)

fake = faker.Faker()
generators = {}
user_ids = []
airplanes = []
pilots = []
flights = []


def generators_sort():
    """Sort generators dictionary by dependencies."""
    visited = set()
    stack = {}
    global generators

    def dfs(node):
        if node in visited:
            return
        visited.add(node)

        if node in generators:
            for dependency in generators[node][0]:
                dfs(dependency)

            stack[node] = generators[node]

    for node in generators:
        dfs(node)

    generators = stack


def register(deps: list = None):
    """Register function in generators dictionary and call
    sorting function.
    :param deps:
    :return:
    """
    if deps is None:
        deps = []

    def decorator(func):
        generators[func.__name__] = (deps, func)

        generators_sort()
        return func
    return decorator


@register()
def create_fake_user():
    """Create 2 fake users."""
    roles = ['customer', 'supervisor']
    with transaction.atomic():
        for role in roles:
            user_data = fake.profile()
            first_name, last_name = user_data['name'].split(maxsplit=1)
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['mail'],
                first_name=first_name,
                last_name=last_name,
                bio=fake.paragraph(nb_sentences=4),
                role=role
            )
            user_ids.append(user.id)


@register()
def create_fake_airports():
    """Create 2 fake airport instances."""
    airports = [('Borispil', 'KBP'), ('Zhuliany', 'IEV')]
    with transaction.atomic():
        for airport in airports:
            Airport.objects.create(
                name=airport[0],
                city='Kyiv',
                country='Ukraine',
                IATA_code=airport[1]
            )


@register()
def create_fake_pilots():
    """Create 2 fake pilot instances."""
    with transaction.atomic():
        for _ in range(2):
            pilot = Pilot.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                category='ATP',
                email=fake.email()
            )
            pilots.append(pilot)


@register()
def create_fake_seat_type():
    """Create 2 fake seat type instances."""
    seat_types = [('Economy', 1.0), ('Business', 2.5)]
    with transaction.atomic():
        for seat_type in seat_types:
            SeatType.objects.create(
                seat_type=seat_type[0],
                price_multiplier=seat_type[1]
            )


def fake_airplane_number():
    """Create fake plane number"""
    number = fake.random_uppercase_letter() + fake.random_uppercase_letter()
    return number + str(fake.random_number(digits=3, fix_len=True))


@register()
def create_fake_airplane():
    """Create fake airplane instance."""
    airplane = Airplane.objects.create(
        number=fake_airplane_number()
    )
    airplanes.append(airplane)


@register(deps=['create_fake_airplane', 'create_fake_seat_type'])
def create_fake_seats():
    """Create fake seat instances for created fake plane."""
    eco_class = SeatType.objects.get(seat_type='Economy')
    business_class = SeatType.objects.get(seat_type='Business')
    with transaction.atomic():
        for row in range(1, 3):
            for seat in ['A', 'B', 'C', 'D']:
                Seat.objects.create(
                    number=seat + str(row),
                    seat_type=business_class,
                    airplane=airplanes[0]
                )
        for row in range(3, 11):
            for seat in ['A', 'B', 'C', 'D', 'E', 'F']:
                Seat.objects.create(
                    number=seat + str(row),
                    seat_type=eco_class,
                    airplane=airplanes[0]
                )


@register(deps=['create_fake_user', 'create_fake_airports',
                'create_fake_pilots'])
def create_fake_flight():
    """Create fake flight instance."""
    flight = Flight(
        number=fake_airplane_number(),
        ticket_price=50,
        boarding_time=datetime(2023, 9, 20, 15, 15),
        departure_time=datetime(2023, 9, 20, 16, 15),
        arrival_time=datetime(2023, 9, 20, 17, 5),
        distance=80,
        airplane=airplanes[0],
        created_by=User.objects.get(role='supervisor'),
        departure_airport=Airport.objects.get('Borispil'),
        destination_airport=Airport.objects.get('Zhuliany')
    )
    flight.pilots.add(*pilots)
    flight.save()
    flights.append(flight)


@register()
def create_fake_discount():
    """Create fake discount instance."""
    Discount.objects.create(
        name='Opening discount',
        is_percentage=True,
        amount=15,
        promo_code='openair2023'
    )


@register()
def create_fake_options():
    """Create 2 fake option instances"""
    options = [('luggage', 20), ('lunch', 15)]
    with transaction.atomic():
        for option in options:
            Option.objects.create(
                name=option[0],
                price=option[1]
            )


@register()
def create_fake_passenger():
    """Crate fake passenger instance."""
    Passenger.objects.create(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        passport_number='AB123456'
    )


@register(deps=['create_fake_user'])
def create_fake_purchase():
    """Create fake purchase instance."""
    Purchase.objects.create(
        is_paid=False,
        user=User.objects.get(role='customer')
    )


@register(deps=['create_fake_seats'])
def create_fake_tickets():
    """Create fake tickets for fake flight."""
    with transaction.atomic():
        for seat in flights[0].airplane.seats.all():
            Ticket.objects.create(
                ticket_code=str(fake.random_number(digits=9, fix_len=True)),
                seat=seat,
            )


class Command(BaseCommand):
    """CLI command for adding fake users with fake subscriptions."""
    help = 'Add 2 fake users with fake subscriptions.'

    def handle(self, *args, **options):
        for name, (deps, func) in generators.items():
            func()
        self.stdout.write(
            self.style.SUCCESS('Successfully created.'))

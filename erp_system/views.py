import json
import string
import secrets

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db import IntegrityError, transaction

from .models import Flight, Ticket, SeatType, Seat, Airplane, Pilot, User, Option
from .forms import CreateFlight, CreatePilot, CreateManager, CreatePlane, CreateOption


def staff_flights(request):
    """Show all flights."""
    flights = Flight.objects.order_by('-boarding_time')
    return render(request, 'erp_system/staff_flights.html', {
        'flights': flights
    })


def send_pilot_assigning_letter(flight):
    """Inform a pilot that he was assigned to a flight."""
    subject = "You were assigned to aflight."
    for pilot in flight.pilots.all():
        message = render_to_string('letters/assigning_pilots_to_flight.html', {
            'pilot': pilot,
            'flight': flight
        })
        mail = EmailMessage(subject, message, to=[pilot.email])
        mail.send()


def create_flight(request):
    """Create flight and tickets for that flight."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to create flights.')
        return redirect('erp_system:staff_flights')
    if request.method == 'GET':
        return render(request, 'erp_system/create_flight.html', {
            'flight_form': CreateFlight()
        })
    flight_form = CreateFlight(request.POST)
    if flight_form.is_valid():
        flight = flight_form.save()
        for seat in flight.airplane.seats.all():
            Ticket.objects.create(
                ticket_code=f'{flight.number}-{seat.number}',
                seat=seat,
                flight=flight
            )
        send_pilot_assigning_letter(flight)
        messages.success(request, 'Flight was created successfully!')
        return redirect('erp_system:staff_flights')
    for error in json.loads(flight_form.errors.as_json()).values():
        messages.error(request, error[0]['message'])
    return render(request, 'erp_system/create_flight.html', {
        'flight_form': CreateFlight(request.POST)
    })


def staff_airplanes(request):
    """Show all planes. Only for supervisors."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to watch airplanes'
                               'list.')
        return redirect('erp_system:staff_flights')
    airplanes = Airplane.objects.all()
    return render(request, 'erp_system/staff_airplanes.html', {
        'airplanes': airplanes
    })


def create_plane_and_seats(
        plane_num: str, business_rows: int, business_seats: int,
        economy_rows: int, economy_seats: int):
    """Create plane with seats."""
    economy = SeatType.objects.get(seat_type='Economy')
    business = SeatType.objects.get(seat_type='Business')
    plane = Airplane.objects.create(number=plane_num)
    with transaction.atomic():
        for row in range(1, business_rows + 1):
            for seat in string.ascii_uppercase[:business_seats]:
                Seat.objects.create(
                    number=seat + str(row),
                    seat_type=business,
                    airplane=plane
                )
        for row in range(business_rows + 1,
                         economy_rows + business_rows + 1):
            for seat in string.ascii_uppercase[:economy_seats]:
                Seat.objects.create(
                    number=seat + str(row),
                    seat_type=economy,
                    airplane=plane
                )


def create_plane_view(request):
    """Create a plane. Give permission only for a supervisor.
    Create seats for a plane."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to create airplanes.')
        return redirect('erp_system:staff_flights')
    if request.method == 'GET':
        return render(request, 'erp_system/create_airplane.html', {
            'creation_form': CreatePlane
        })
    if CreatePlane(request.POST).is_valid():
        create_plane_and_seats(request.POST['number'],
                               int(request.POST['business_seat_rows']),
                               int(request.POST['business_seats_in_row']),
                               int(request.POST['economy_seat_rows']),
                               int(request.POST['economy_seats_in_row']))
        return redirect('erp_system:staff_planes')
    return render(request, 'erp_system/create_airplane.html', {
        'creation_form': CreatePlane(request.POST)
    })


def staff_pilot(request):
    """Show all pilots. Only for supervisors."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to see pilots list.')
        return redirect('erp_system:staff_flights')
    pilots = Pilot.objects.all()
    return render(request, 'erp_system/staff_pilots.html', {
        'pilots': pilots
    })


def create_pilot(request):
    """Create a pilot."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to create pilots.')
        return redirect('erp_system:staff_flights')
    if request.method == 'GET':
        return render(request, 'erp_system/create_pilot.html', {
            'pilot_form': CreatePilot
        })
    pilot_form = CreatePilot(request.POST)
    if pilot_form.is_valid():
        pilot_form.save()
        return redirect('erp_system:staff_pilots')
    return render(request, 'erp_system/create_pilot.html', {
        'pilot_form': pilot_form
    })


def staff_managers(request):
    """Show all managers. Only for supervisors."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to see managers '
                               'list.')
        return redirect('erp_system:staff_flights')
    managers = User.objects.filter(role__in=['gate_manager',
                                             'check_in_manager'])
    return render(request, 'erp_system/staff_managers.html', {
        'managers': managers
    })


def send_manager_assigning_letter(manager, password: str):
    """Sent email to manager whose was assigned."""
    subject = "Welcome to Django AIR team"
    message = render_to_string('letters/manager_assigning_letter.html', {
        'manager': manager,
        'password': password
    })
    mail = EmailMessage(subject, message, to=[manager.email])
    mail.send()


def create_manager(request):
    """Create a manager."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to create managers.')
        return redirect('erp_system:staff_flights')
    if request.method == 'GET':
        return render(request, 'erp_system/create_manager.html', {
            'manager_form': CreateManager()
        })
    try:
        chars = string.digits + string.ascii_letters
        random_password = ''.join([secrets.choice(chars) for _ in range(12)])
        manager = User.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            role=request.POST['role'],
            password=random_password
        )
        send_manager_assigning_letter(manager, random_password)
        return redirect('erp_system:staff_managers')
    except IntegrityError:
        return render(request, 'erp_system/create_manager.html', {
            'manager_form': CreateManager(request.POST)
        })


def staff_options(request):
    """Show all options. Only for supervisors."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to see options '
                               'list.')
        return redirect('erp_system:staff_flights')
    options = Option.objects.all()
    return render(request, 'erp_system/staff_options.html', {
        'options': options
    })


def create_option(request):
    """Create an option."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to create options.')
        return redirect('erp_system:staff_flights')
    if request.method == 'GET':
        return render(request, 'erp_system/create_option.html', {
            'creation_form': CreateOption()
        })
    option_form = CreateOption(request.POST)
    if option_form.is_valid():
        option_form.save()
        return redirect('erp_system:staff_options')
    return render(request, 'erp_system/create_option.html', {
        'creation_form': option_form
    })


# todo
def check_in_manager_menu(request):
    """Find a ticket by number and redirect to page with check-in."""
    if request.user.role not in ['supervisor', 'check_in_manager']:
        messages.info(request, 'You are not allowed to check-in passengers.')
        return redirect('erp_system:staff_flights')
    if request.method == "GET":
        return render(request, 'erp_system/check_in_menu.html')
    ticket = Ticket.objects.get(number=request.POST['ticket_number'])
    return redirect('')


# todo
def ticket_check_in(request, ticket_id):
    """Check-in the ticket. Manager also can add options to a ticket."""

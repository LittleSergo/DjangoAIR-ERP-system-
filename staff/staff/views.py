import json
import string
import secrets
from copy import copy

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from common_instances.models import (
    Flight, Ticket, SeatType, Seat, Option, Discount, Airplane
)
from .tasks import (
    send_pilot_assigning_letter, send_manager_assigning_letter,
    send_password_reset_email, PASSWORD_RESET_TOKEN_GENERATOR
)
from .models import Pilot, User
from .forms import (
    CreateFlight, CreatePilot, CreateManager, CreatePlane,
    CreateOption, CheckInForm, CreateDiscount
)
from common_instances.forms import ResetPasswordForm


@login_required
def staff_flights(request):
    """Show all flights."""
    flights = Flight.objects.order_by('-boarding_time')
    return render(request, 'staff/staff_flights.html', {
        'flights': flights
    })


@login_required
def create_flight(request):
    """Create flight and tickets for that flight."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to create flights.')
        return redirect('staff:staff_flights')
    if request.method == 'GET':
        return render(request, 'staff/create_flight.html', {
            'flight_form': CreateFlight()
        })
    flight_form = CreateFlight(request.POST)
    if flight_form.is_valid():
        flight = flight_form.save()
        for pilot in flight_form.cleaned_data['pilots']:
            pilot.flights.add(flight)
        for seat in flight.airplane.seats.all():
            Ticket.objects.create(
                ticket_code=f'{flight.number}-{seat.number}',
                seat=seat,
                flight=flight
            )
        send_pilot_assigning_letter.delay(flight.id)
        messages.success(request, 'Flight was created successfully!')
        return redirect('staff:staff_flights')
    for error in json.loads(flight_form.errors.as_json()).values():
        messages.error(request, error[0]['message'])
    return render(request, 'staff/create_flight.html', {
        'flight_form': CreateFlight(request.POST)
    })


@login_required
def staff_airplanes(request):
    """Show all planes. Only for supervisors."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to watch airplanes'
                               'list.')
        return redirect('staff:staff_flights')
    airplanes = Airplane.objects.all()
    return render(request, 'staff/staff_airplanes.html', {
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


@login_required
def create_plane_view(request):
    """Create a plane. Give permission only for a supervisor.
    Create seats for a plane."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to create airplanes.')
        return redirect('staff:staff_flights')
    if request.method == 'GET':
        return render(request, 'staff/create_airplane.html', {
            'creation_form': CreatePlane
        })
    if CreatePlane(request.POST).is_valid():
        create_plane_and_seats(request.POST['number'],
                               int(request.POST['business_seat_rows']),
                               int(request.POST['business_seats_in_row']),
                               int(request.POST['economy_seat_rows']),
                               int(request.POST['economy_seats_in_row']))
        messages.success(request, 'Plane was created successfully.')
        return redirect('staff:staff_planes')
    return render(request, 'staff/create_airplane.html', {
        'creation_form': CreatePlane(request.POST)
    })


@login_required
def staff_pilot(request):
    """Show all pilots. Only for supervisors."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to see pilots list.')
        return redirect('staff:staff_flights')
    pilots = Pilot.objects.all()
    return render(request, 'staff/staff_pilots.html', {
        'pilots': pilots
    })


@login_required
def create_pilot(request):
    """Create a pilot."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to create pilots.')
        return redirect('staff:staff_flights')
    if request.method == 'GET':
        return render(request, 'staff/create_pilot.html', {
            'pilot_form': CreatePilot
        })
    pilot_form = CreatePilot(request.POST)
    if pilot_form.is_valid():
        pilot_form.save()
        return redirect('staff:staff_pilots')
    return render(request, 'staff/create_pilot.html', {
        'pilot_form': pilot_form
    })


@login_required
def staff_managers(request):
    """Show all managers. Only for supervisors."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to see managers '
                               'list.')
        return redirect('staff:staff_flights')
    managers = User.objects.filter(role__in=['gate_manager',
                                             'check_in_manager'])
    return render(request, 'staff/staff_managers.html', {
        'managers': managers
    })


@login_required
def create_manager(request):
    """Create a manager."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to create managers.')
        return redirect('staff:staff_flights')
    if request.method == 'GET':
        return render(request, 'staff/create_manager.html', {
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
        send_manager_assigning_letter.delay(manager.id, random_password)
        return redirect('staff:staff_managers')
    except IntegrityError:
        return render(request, 'staff/create_manager.html', {
            'manager_form': CreateManager(request.POST)
        })


@login_required
def staff_options(request):
    """Show all options. Only for supervisors."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to see options '
                               'list.')
        return redirect('staff:staff_flights')
    options = Option.objects.all()
    return render(request, 'staff/staff_options.html', {
        'options': options
    })


@login_required
def create_option(request):
    """Create an option."""
    if request.user.role != 'supervisor':
        messages.info(request,
                      'You are not allowed to create options.')
        return redirect('staff:staff_flights')
    if request.method == 'GET':
        return render(request, 'staff/create_option.html', {
            'creation_form': CreateOption()
        })
    option_form = CreateOption(request.POST)
    if option_form.is_valid():
        option_form.save()
        return redirect('staff:staff_options')
    return render(request, 'staff/create_option.html', {
        'creation_form': option_form
    })


@login_required
def staff_discounts(request):
    """Show all discounts."""
    if request.user.role != 'supervisor':
        messages.info(request, 'You are not allowed to see discounts '
                               'list.')
        return redirect('staff:staff_flights')
    if request.method == 'GET':
        discounts = Discount.objects.all()
        return render(request, 'staff/staff_discounts.html', {
            'discounts': discounts
        })


@login_required
def create_discount(request):
    """Create a discount."""
    if request.user.role != 'supervisor':
        messages.info(request,
                      'You are not allowed to create discount.')
        return redirect('staff:staff_flights')
    if request.method == 'GET':
        return render(request, 'staff/create_discount.html', {
            'creation_form': CreateDiscount
        })
    CreateDiscount(request.POST).save()
    messages.success(request, 'Discount created successfully.')
    return redirect('staff:staff_discounts')


@login_required
def check_in_manager_menu(request):
    """Find a ticket by number and redirect to page with check-in."""
    if request.user.role not in ['supervisor', 'check_in_manager']:
        messages.info(request,
                      'You are not allowed to check-in passengers.')
        return redirect('staff:staff_flights')
    if request.method == "GET":
        return render(request, 'staff/check_in_menu.html')
    ticket = Ticket.objects.filter(
        ticket_code=request.POST['ticket_code']
    )
    if not ticket:
        messages.info(request, 'That ticket does not exist.')
        return render(request, 'staff/check_in_menu.html')
    return redirect('staff:ticket_check_in', ticket[0].id)


def check_for_new_options(options_before_check_in, options_after_check_in):
    """Check is there a new options in ticket after check-in.
    :param options_after_check_in:
    :param options_before_check_in:
    :return: price of new options
    """
    options_fee = 0
    for option in options_after_check_in:
        if option not in options_before_check_in:
            options_fee += option.price
    return options_fee


@login_required
def ticket_check_in(request, ticket_id):
    """Check-in the ticket. Manager also can add options to a ticket."""
    if request.user.role not in ['supervisor', 'check_in_manager']:
        messages.info(request,
                      'You are not allowed to check-in passengers.')
        return redirect('staff:staff_flights')
    ticket = Ticket.objects.get(id=ticket_id)
    if request.method == 'GET':
        return render(request, 'staff/ticket_check-in.html', {
            'ticket': ticket,
            'check_in_form': CheckInForm(instance=ticket),
        })
    options_before_check_in = copy(ticket.options.all())
    ticket = CheckInForm(request.POST, instance=ticket).save()
    options_fee = check_for_new_options(
        options_before_check_in, ticket.options.all()
    )
    if options_fee > 0:
        messages.info(request, f'Take {options_fee} EUR fee for options '
                               f'from the passenger.')
    ticket.checked_in = True
    ticket.save()
    messages.success(request, 'Passenger checked-in successful.')
    return redirect('staff:check_in_menu')


@login_required
def boarding_menu(request):
    """Find a ticket by number and redirect to page with boarding."""
    if request.user.role not in ['supervisor', 'check_in_manager']:
        messages.info(request,
                      'You are not allowed to board passengers.')
        return redirect('staff:staff_flights')
    if request.method == "GET":
        return render(request, 'staff/boarding_menu.html')
    ticket = Ticket.objects.filter(ticket_code=request.POST['ticket_code'])
    if not ticket:
        messages.info(request, 'That ticket does not exist.')
        return render(request, 'staff/boarding_menu.html')
    return redirect('staff:passenger_boarding', ticket[0].id)


@login_required
def boarding_passenger(request, ticket_id):
    """Show the passenger data and board him."""
    if request.user.role not in ['supervisor', 'check_in_manager']:
        messages.info(request,
                      'You are not allowed to board passengers.')
        return redirect('staff:staff_flights')
    ticket = Ticket.objects.get(id=ticket_id)
    if request.method == "GET":
        return render(request, 'staff/boarding_passenger.html', {
            'ticket': ticket
        })
    ticket.is_on_board = True
    ticket.save()
    messages.success(request, 'Ticket boarded on successfully.')
    return redirect('staff:boarding_menu')


def login_user(request):
    """Login user page.
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'staff/login.html',
                      {'form': AuthenticationForm()})

    user = authenticate(request, username=request.POST['username'],
                        password=request.POST['password'])

    if user is None:
        messages.error(request, 'Username and password did not match.')
        return render(request, 'staff/login.html', {
            'form': AuthenticationForm()
        })
    # Managers receive their credentials by emails and first
    # login will verify their email
    if not user.email_is_verified:
        user.email_is_verified = True
        user.save()
    messages.success(request, f"Successfully logged in as {user.username}.")
    login(request, user)
    return redirect('staff:staff_flights')


@login_required
def logout_user(request):
    """Log out user functionality.
    :param request:
    :return:
    """
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Successfully logged out.')
        return redirect('staff:log_in')


@login_required
def profile(request, user_id):
    """Show user profile."""
    user = User.objects.get(pk=user_id)
    if request.method == 'GET':
        if request.user != user and request.user.role != 'supervisor':
            messages.info(request, 'You can not see another user profile.')
            return redirect('staff:profile', request.user.id)
        return render(request, 'staff/profile.html', {
            'user': user
        })

    if user.check_password(request.POST['password']):
        domain = get_current_site(request).domain
        send_password_reset_email(domain, request.is_secure(), user.id)
        messages.success(request, 'Email with instructions was sent on '
                                  'your email.')
        return render(request, 'staff/profile.html', {
            'user': user
        })
    messages.error(request, 'Wrong password, try again.')
    return render(request, 'staff/profile.html', {
        'user': user
    })


def change_password(request, uidb64, token):
    """Send an email with instructions for password changing.
    :param request:
    :param uidb64:
    :param token:
    :return:
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except ObjectDoesNotExist:
        user = None

    if user and PASSWORD_RESET_TOKEN_GENERATOR.check_token(user, token):
        if request.method == 'GET':
            return render(request, 'staff/reset_password.html', {
                'form': ResetPasswordForm
            })
        if ResetPasswordForm(request.POST).is_valid():
            user.set_password(request.POST['password'])
            user.save()
            messages.success(request, 'Password was changed successfully.')
            return redirect('staff:profile', user.id)

        return render(request, 'staff/reset_password.html', {
            'form': ResetPasswordForm(request.POST)
        })
    messages.info(request, 'That user does not exist or token is not '
                           'valid. Please start the procedure for '
                           'creating a new password again.')
    return redirect('staff:staff_flights')

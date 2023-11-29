import logging
import paypalrestsdk
import datetime

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.urls import reverse

from pytz import timezone

from common_instances.models import Flight, Passenger, Discount
from common_instances.forms import ResetPasswordForm
from .forms import (
    SignupForm, CheckInFormSet, SearchForFlightsForm,
    build_formset_with_definite_forms
)
from .models import Purchase
from .payment_methods import paypal_payment
from .tasks import (
    PASSWORD_RESET_TOKEN_GENERATOR, send_password_reset_email,
    send_email_with_receipt_and_ticket
)

User = get_user_model()


def signup(request):
    """Signup page."""
    if request.method == 'GET':
        return render(request, 'client/signup.html', {
            'form': SignupForm
        })
    form = SignupForm(request.POST)
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(request.POST['password'])
        user.save()
        messages.success(request, 'Your account wes successfully created!')
        return redirect('client:login')
    return render(request, 'client/signup.html', {
        'form': form
    })


def login_view(request):
    """Login page."""
    if request.method == 'GET':
        return render(request, 'client/login.html', {
            'form': AuthenticationForm
        })

    user = authenticate(request, username=request.POST['username'],
                        password=request.POST['password'])

    if user is None:
        messages.error(request, 'Username and password did not match.')
        return render(request, 'client/login.html', {
            'form': AuthenticationForm(request.POST)
        })

    messages.success(request, f"Successfully logged in as {user.username}.")
    login(request, user)
    return redirect('client:home')


@login_required
def logout_user(request):
    """Log out user functionality.
    :param request:
    :return:
    """
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Successfully logged out.')
        return redirect('client:login')


def sort_purchases(purchases):
    """Sort purchases onto purchases with future and previous flights."""
    future_flights = []
    previous_flights = []
    for purchase in purchases:
        if purchase.tickets.all()[0].flight.departure_time > \
                datetime.datetime.now(tz=timezone('EET')):
            future_flights.append(purchase)
            purchases.exclude(id=purchase.id)
            continue
        previous_flights.append(purchase)

    return future_flights, previous_flights


@login_required
def user_profile(request):
    """View for users profile. Show user information with previous
    and future flights."""
    if request.method == 'GET':
        future_flights, previous_flights = sort_purchases(
            request.user.purchases.all()
        )
        return render(request, 'client/profile.html', {
            'user': request.user,
            'future_flights': future_flights,
            'previous_flights': previous_flights
        })

    if request.user.check_password(request.POST['password']):
        domain = get_current_site(request).domain
        send_password_reset_email.delay(domain, request.is_secure(),
                                        request.user.id)
        messages.success(request, 'Email with instructions was sent on '
                                  'your email.')
        return redirect('client:profile')
    messages.error(request, 'Wrong password, try again.')
    return redirect('client:profile')


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
            return render(request, 'client/reset_password.html', {
                'form': ResetPasswordForm
            })
        if ResetPasswordForm(request.POST).is_valid():
            user.set_password(request.POST['password'])
            user.save()
            messages.success(request, 'Password was changed successfully.')
            return redirect('client:profile')

        return render(request, 'client/reset_password.html', {
            'form': ResetPasswordForm(request.POST)
        })
    messages.info(request, 'That user does not exist or token is not '
                           'valid. Please start the procedure for '
                           'creating a new password again.')
    return redirect('client:profile')


@login_required
def online_checkin(request, purchase_id):
    """View for online check-in for passengers."""
    purchase = Purchase.objects.get(id=purchase_id)
    formset = CheckInFormSet(queryset=purchase.tickets.all())
    if request.method == 'GET':
        return render(request, 'client/online_checkin.html', {
            'formset': formset
        })

    with transaction.atomic():
        for ticket in purchase.tickets.all():
            ticket.checked_in = True
            ticket.save()
    messages.success(request, 'Your tickets were checked in successfully!')
    return redirect('client:profile')


@login_required
def home(request):
    """View for home page with form for flights searching."""
    if request.method == "GET":
        return render(request, 'client/home.html', {
            'form': SearchForFlightsForm
        })
    form = SearchForFlightsForm(request.POST)
    if form.is_valid():
        return redirect(
            reverse('client:flights_search') +
            f"?from={form.data['arriving']}"
            f"&to={form.data['destination']}"
            f"&day={form.data['date_day']}"
            f"&month={form.data['date_month']}"
            f"&year={form.data['date_year']}"
            f"&passengers={form.data['passengers']}"
        )
    return render(request, 'client/home.html', {
        'form': form
    })


@login_required
def flights_search(request):
    """Show all suitable to parameters flights."""
    if request.method == 'GET':
        flights = Flight.objects.filter(
            departure_airport=request.GET.get('from', ''),
            destination_airport=request.GET.get('to', ''),
            departure_time__year=request.GET.get('year', ''),
            departure_time__month=request.GET.get('month', ''),
            departure_time__day=request.GET.get('day', '')
        )
        return render(request, 'client/flights_search.html', {
            'flights': flights,
            'passengers': request.GET.get('passengers', '')
        })


def find_or_create_passenger(passport, firs_name, last_name):
    """Find and return passenger if exists, else create new one.
    :param passport:
    :param firs_name:
    :param last_name:
    :return:
    """
    passenger = Passenger.objects.filter(passport_number=passport)
    if passenger.exists():
        return passenger[0]
    return Passenger.objects.create(
        passport_number=passport,
        first_name=firs_name,
        last_name=last_name
    )


def ticket_appropriation(form, ticket, purchase):
    """Assign passenger to a ticket, add options and make ticket
    unavailable.
    :param form:
    :param ticket:
    :param purchase:
    :return:
    """
    discount = Discount.objects.filter(
        promo_code=form.cleaned_data['promo_code'],
    )
    if discount.exists():
        ticket.discount = discount[0]
    ticket.passenger = find_or_create_passenger(
        form.cleaned_data['passport_number'],
        form.cleaned_data['first_name'],
        form.cleaned_data['last_name']
    )
    ticket.options.set(form.cleaned_data['options'])
    ticket.is_available = False
    ticket.save()
    purchase.tickets.add(ticket)


@login_required
def buy_tickets(request, flight_id):
    """Show forms for info about passengers and tickets.
    And update tickets info if method POST."""
    # If users email isn't verified he can't buy tickets
    if not request.user.email_is_verified:
        messages.info(request,
                      'You can not buy ticket until your email is not '
                      'verified. Please check your mailbox and verify '
                      'your email.')
        return redirect('client:home')
    flight = Flight.objects.get(id=flight_id)
    formset = build_formset_with_definite_forms(
        int(request.GET.get('passengers', 1))
    )
    if request.method == 'GET':
        return render(request, 'client/buy_tickets.html', {
            'formset': formset,
            'flight': flight
        })
    formset = formset(request.POST)
    if formset.is_valid():
        # Create purchase, payment and save data about passenger and
        # his ticket settings.
        purchase = Purchase.objects.create(
            user=request.user
        )
        for form in formset:
            ticket = flight.tickets.filter(
                is_available=True,
                seat__seat_type=form.cleaned_data['seat_class']
            ).first()
            if not ticket:
                messages.info(
                    request,
                    f"Ran out of {form.cleaned_data['seat_class']} "
                    f"tickets on this flight."
                )
                return render(request, 'client/buy_tickets.html', {
                    'formset': formset,
                    'flight': flight
                })
            ticket_appropriation(form, ticket, purchase)
        purchase.save()
        return redirect('client:checkout', purchase.id)
    return render(request, 'client/buy_tickets.html', {
        'formset': formset,
        'flight': flight
    })


@login_required
def checkout_view(request, purchase_id):
    """Show total bill for tickets.
    :param request:
    :param purchase_id:
    :return:
    """
    if request.method == 'GET':
        purchase = Purchase.objects.get(id=purchase_id)
        return render(request, 'client/checkout.html', {
            'purchase': purchase,
        })


@login_required
def create_payment(request, purchase_id: int,
                   payment_method: str = 'paypal'):
    """Create payment and redirect to payment page,
    or to payment failed page if payment is failed.
    :param payment_method:
    :param request:
    :param purchase_id:
    :return:
    """
    if payment_method == 'paypal':
        return paypal_payment(request, purchase_id)


@login_required
def execute_payment(request, purchase_id):
    """Check is payment successful or not and redirect to
    appropriate page.
    :param request:
    :param purchase_id:
    :return:
    """
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        return redirect('client:payment_success', purchase_id)
    logger = logging.getLogger('django')
    logger.error(
        f"{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        f" - Payment error: {payment.error}"
    )
    return redirect('client:payment_failed', purchase_id)


@login_required
def payment_success(request, purchase_id):
    """Set purchase is paid to true and redirect to profile page with
    message about successful payment.
    :param request:
    :param purchase_id:
    :return:
    """
    send_email_with_receipt_and_ticket.delay(purchase_id)
    messages.success(request, 'Payment succeed. Have a nice flight!')
    return redirect('client:profile')


@login_required
def payment_failed(request, purchase_id):
    """Redirect to check out page with message about failed payment.
    :param request:
    :param purchase_id:
    :return:
    """
    messages.info(request, 'Payment failed! Please try again.')
    return redirect('client:checkout', purchase_id)

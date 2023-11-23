from datetime import datetime, timedelta
from pytz import timezone

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from common_instances.models import Flight
from django_air.celery import app

from staff.models import Pilot, User

PASSWORD_RESET_TOKEN_GENERATOR = PasswordResetTokenGenerator()


@app.task
def send_manager_assigning_letter(manager_id, password: str):
    """Sent email to manager whose was assigned."""
    manager = User.objects.get(id=manager_id)
    subject = "Welcome to Django AIR team"
    message = render_to_string('staff/letters/manager_assigning_letter.html', {
        'manager': manager,
        'password': password
    })
    mail = EmailMessage(subject, message, to=[manager.email])
    mail.send()


@app.task
def send_pilot_assigning_letter(flight_id):
    """Inform a pilot that he was assigned to a flight."""
    flight = Flight.objects.get(id=flight_id)
    subject = "You were assigned to a flight."
    for pilot in flight.pilots.all():
        message = render_to_string('staff/letters/assigning_pilots_to_flight.html', {
            'pilot': pilot,
            'flight': flight
        })
        mail = EmailMessage(subject, message, to=[pilot.email])
        mail.send()


@app.task
def send_password_reset_email(domain, request_is_secure: bool, user_id):
    """Send an email with instructions for password changing.
    :param domain:
    :param request_is_secure:
    :param user_id:
    :return:
    """
    user = User.objects.get(id=user_id)
    mail_subject = "Reset password."
    message = render_to_string("staff/letters/reset_password_letter.html", {
        'user': user,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user_id)),
        'token': PASSWORD_RESET_TOKEN_GENERATOR.make_token(user),
        'protocol': 'https' if request_is_secure else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.send()


@app.task
def send_flight_reminder_to_pilot(pilot_id, flight_id):
    """Remind the pilot about coming flight via email."""
    pilot = Pilot.objects.get(id=pilot_id)
    flight = Flight.objects.get(id=flight_id)
    mail_subject = "DjangoAIR - flight reminder."
    message = render_to_string("staff/letters/flight_reminder.html", {
        'pilot': pilot,
        'flight': flight
    })
    mail = EmailMessage(mail_subject, message, to=[pilot.email])
    mail.send()


@app.task
def flight_pilot_reminder():
    """Find coming flights and send email remind to the pilots."""
    flights = Flight.objects.filter(
        pilots_reminder_is_sent=False,
        departure_time__gte=datetime.now(tz=timezone('EET')),
        departure_time__lte=(datetime.now(tz=timezone('EET'))
                             + timedelta(hours=6))
    )
    for flight in flights:
        for pilot in flight.pilots.all():
            send_flight_reminder_to_pilot.delay(pilot.id, flight.id)
        flight.pilots_reminder_is_sent = True
        flight.save()

from django.contrib import admin

from .models import (
    User, Flight, Pilot, Airport, Purchase, Passenger, Ticket, Seat,
    Airplane, Option, Discount, SeatType
)

admin.site.register(User)
admin.site.register(Flight)
admin.site.register(Pilot)
admin.site.register(Airport)
admin.site.register(Purchase)
admin.site.register(Passenger)
admin.site.register(Ticket)
admin.site.register(Seat)
admin.site.register(SeatType)
admin.site.register(Airplane)
admin.site.register(Option)
admin.site.register(Discount)

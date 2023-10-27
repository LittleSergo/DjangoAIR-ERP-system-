from django.contrib import admin

from .models import (
    Flight, Airport, Passenger, Ticket, Seat,
    Option, Discount, SeatType, Airplane
)

admin.site.register(Flight)
admin.site.register(Airport)
admin.site.register(Passenger)
admin.site.register(Ticket)
admin.site.register(Seat)
admin.site.register(SeatType)
admin.site.register(Option)
admin.site.register(Discount)
admin.site.register(Airplane)

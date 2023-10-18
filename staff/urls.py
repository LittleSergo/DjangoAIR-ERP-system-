from django.urls import path, include

from . import views

app_name = 'staff'

flight_urlpatterns = [
    path('', views.staff_flights, name='staff_flights'),
    path('create/', views.create_flight, name='create_flight'),
]

airplanes_urlpatterns = [
    path('', views.staff_airplanes, name='staff_planes'),
    path('create/', views.create_plane_view, name='create_airplane'),
]

pilots_urlpatterns = [
    path('', views.staff_pilot, name='staff_pilots'),
    path('create/', views.create_pilot, name='create_pilot'),
]

managers_urlpatterns = [
    path('', views.staff_managers, name='staff_managers'),
    path('create/', views.create_manager, name='create_manager'),
]

options_urlpatterns = [
    path('', views.staff_options, name='staff_options'),
    path('create/', views.create_option, name='create_option'),
]

discounts_urlpatterns = [
    path('', views.staff_discounts, name='staff_discounts'),
    path('create/', views.create_discount, name='create_discount'),
]

check_in_urlpatterns = [
    path('', views.check_in_manager_menu, name='check_in_menu'),
    path('tickets/<ticket_id>', views.ticket_check_in,
         name='ticket_check_in'),
]

boarding_urlpatterns = [
    path('', views.boarding_menu, name='boarding_menu'),
    path('tickets/<ticket_id>', views.boarding_passenger,
         name='passenger_boarding')
]

urlpatterns = [
    path('flights/', include(flight_urlpatterns)),
    path('airplanes/', include(airplanes_urlpatterns)),
    path('pilots/', include(pilots_urlpatterns)),
    path('managers/', include(managers_urlpatterns)),
    path('options/', include(options_urlpatterns)),
    path('discounts/', include(discounts_urlpatterns)),
    path('check-in/', include(check_in_urlpatterns)),
    path('boarding/', include(boarding_urlpatterns)),
]

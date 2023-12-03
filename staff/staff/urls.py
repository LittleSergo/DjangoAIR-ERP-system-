from django.urls import path, include

from . import views

app_name = 'staff'

flight_urls = [
    path('', views.staff_flights, name='staff_flights'),
    path('create/', views.create_flight, name='create_flight'),
]

airplanes_urls = [
    path('', views.staff_airplanes, name='staff_planes'),
    path('create/', views.create_plane_view, name='create_airplane'),
]

pilots_urls = [
    path('', views.staff_pilot, name='staff_pilots'),
    path('create/', views.create_pilot, name='create_pilot'),
]

managers_urls = [
    path('', views.staff_managers, name='staff_managers'),
    path('create/', views.create_manager, name='create_manager'),
]

options_urls = [
    path('', views.staff_options, name='staff_options'),
    path('create/', views.create_option, name='create_option'),
]

discounts_urls = [
    path('', views.staff_discounts, name='staff_discounts'),
    path('create/', views.create_discount, name='create_discount'),
]

check_in_urls = [
    path('', views.check_in_manager_menu, name='check_in_menu'),
    path('tickets/<ticket_id>', views.ticket_check_in,
         name='ticket_check_in'),
]

boarding_urls = [
    path('', views.boarding_menu, name='boarding_menu'),
    path('tickets/<ticket_id>', views.boarding_passenger,
         name='passenger_boarding')
]

auth_urls = [
    path('log_in/', views.login_user, name='log_in'),
    path('log_out', views.logout_user, name='log_out')
]

users_urls = [
    path('<user_id>/profile/', views.profile, name='profile'),
    path('profile/change_password/<uidb64>/<token>/', views.change_password,
         name='change_password')
]

urlpatterns = [
    path('flights/', include(flight_urls)),
    path('airplanes/', include(airplanes_urls)),
    path('pilots/', include(pilots_urls)),
    path('managers/', include(managers_urls)),
    path('options/', include(options_urls)),
    path('discounts/', include(discounts_urls)),
    path('check-in/', include(check_in_urls)),
    path('boarding/', include(boarding_urls)),
    path('auth/', include(auth_urls)),
    path('users/', include(users_urls))
]

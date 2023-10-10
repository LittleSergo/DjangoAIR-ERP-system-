from django.urls import path, include

from . import views

app_name = 'erp_system'

staff_urlpatterns = [
    path('flights/', views.staff_flights, name='staff_flights'),
    path('flights/create/', views.create_flight,
         name='create_flight'),
    path('airplanes/', views.staff_airplanes, name='staff_planes'),
    path('airplanes/create/', views.create_plane_view,
         name='create_airplane'),
    path('pilots/', views.staff_pilot, name='staff_pilots'),
    path('pilots/create/', views.create_pilot, name='create_pilot'),
    path('managers/', views.staff_managers, name='staff_managers'),
    path('managers/create/', views.create_manager,
         name='create_manager'),
    path('options/', views.staff_options, name='staff_options'),
    path('options/create/', views.create_option,
         name='create_option'),
    path('check-in/', views.check_in_manager_menu,
         name='check_in_menu'),
    path('check_in/tickets/<id>', views.ticket_check_in,
         name='ticket_check_in'),
]

urlpatterns = [
    path('staff/', include(staff_urlpatterns))
]

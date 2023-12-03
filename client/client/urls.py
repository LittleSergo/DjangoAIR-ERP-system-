from django.urls import path, include

from client import views

app_name = 'client'

auth_urls = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),
]

user_urls = [
    path('profile/', views.user_profile, name='profile'),
    path('profile/change_password/<uidb64>/<token>/',
         views.change_password, name='change_password'),
    path('profile/purchases/<purchase_id>/check-in/',
         views.online_checkin, name='online_checkin'),
]

main_urls = [
    path('', views.home, name='home'),
    path('flights_search/', views.flights_search, name='flights_search'),
    path('flights/<flight_id>/buy_tickets/', views.buy_tickets,
         name='buy_tickets'),
    path('checkout/<purchase_id>/', views.checkout_view, name='checkout'),
]

payment_urls = [
    path('create/<purchase_id>/<payment_method>/', views.create_payment,
         name='create_payment'),
    path('execute/<purchase_id>/', views.execute_payment,
         name='execute_payment'),
    path('success/<purchase_id>/', views.payment_success,
         name='payment_success'),
    path('failed/<purchase_id>/', views.payment_failed,
         name='payment_failed'),
]

urlpatterns = [
    path('auth/', include(auth_urls)),
    path('users/', include(user_urls)),
    path('', include(main_urls)),
    path('payments/', include(payment_urls)),
]

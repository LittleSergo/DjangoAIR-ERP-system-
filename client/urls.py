from django.urls import path, include

from client import views

app_name = 'client'

auth_urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),
]

user_urlpatterns = [
    # path('<user_id>/profile/', name='profile'),
    # path('<user_id>/profile/flights', name='profile_flights'),
    # path('<user_id>/profile/flights/check-in/', name='online_checkin'),
]

main_urlpatterns = [
    # path('', name='home'),
    # path('flights/', name='flights'),
    # path('flights/<flight_id>/tickets/', name='tickets'),
    # path('payment/<payment_id>/', name='payment'),
]

urlpatterns = [
    path('auth/', include(auth_urlpatterns)),
    path('users/', include(user_urlpatterns)),
    path('', include(main_urlpatterns)),
]

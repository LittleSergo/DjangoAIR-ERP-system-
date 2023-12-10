from django.urls import path, include

from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView
)

from client_api import views

router = routers.DefaultRouter()
router.register(r'tickets', views.PurchasedTicketsView)

urlpatterns = [
    path('users/signup/', views.UserSignUpView.as_view()),
    path('users/profile/', views.UserProfileView.as_view()),
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(),
         name='token_verify'),
]

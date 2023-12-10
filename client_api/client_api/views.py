from django.contrib.auth import get_user_model

from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from client_api.serializers import (
    UserRegisterSerializer, PurchasedTicketSerializer,
    UserProfileSerializer
)
from common_instances.models import Ticket


class UserSignUpView(generics.CreateAPIView):
    """User registration view."""
    queryset = get_user_model().objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)


class UserProfileView(APIView):
    """User profile view."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """Return info about logged-in user."""
        return Response(UserProfileSerializer(request.user).data)


class PurchasedTicketsView(viewsets.ReadOnlyModelViewSet):
    """Retrieve and list purchased tickets."""
    queryset = Ticket.objects.all()
    serializer_class = PurchasedTicketSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        """Return list of purchased tickets."""
        tickets = Ticket.objects.filter(
            purchase__user=request.user
        ).order_by('flight__departure_time')
        return Response(
            PurchasedTicketSerializer(tickets, many=True).data
        )

    def retrieve(self, request, pk=None):
        ticket = Ticket.objects.get(id=pk)
        tickets = Ticket.objects.filter(
            purchase__user=request.user
        )
        if ticket in tickets:
            return Response(
                PurchasedTicketSerializer(ticket).data
            )
        return Response(
            {"message": "User dont have access to that ticket."}
        )

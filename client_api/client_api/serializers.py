from django.contrib.auth import get_user_model
from rest_framework import serializers

from common_instances.models import Ticket


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for validation user registration data."""
    class Meta:
        model = get_user_model()
        fields = [
            'username', 'first_name', 'last_name', 'password', 'email'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class PurchasedTicketSerializer(serializers.ModelSerializer):
    """Serializer for purchased tickets."""
    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_code', 'checked_in', 'is_on_board',
            'seat', 'discount', 'options',
            'passenger', 'flight', 'full_price'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for validation user data."""
    class Meta:
        model = get_user_model()
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'email_is_verified'
        ]

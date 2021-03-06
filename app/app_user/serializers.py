from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from core.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user model"""

    password_confirmation = serializers.CharField(
        min_length=5,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        if data.get('password') != data.get('password_confirmation'):
            raise serializers.ValidationError("Those passwords don't match.")

        if data.get('password_confirmation'):
            del data['password_confirmation']

        return data

    class Meta:
        # model = get_user_model()
        model = User
        exclude = ('is_active', 'groups', 'user_permissions',
                   'deleted', 'last_login',)
        extra_kwargs = {
            'name': {'min_length': 5, 'max_length': 255},
            'email': {
                'min_length': 5, 'max_length': 255, },
            'working_id': {'max_length': 255, 'required': False},
            'password': {'write_only': True, 'min_length': 5,
                         'style': {'input_type': 'password'}},
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import ugettext as _
from django.db.models import Count
from rest_framework import serializers
from rest_framework_jwt.compat import PasswordField, Serializer
from rest_framework_jwt.settings import api_settings

from .models import User


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


class UserSerializer(serializers.ModelSerializer):
    company = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['username', 'company', 'email']


def get_email_field():
    try:
        email_field = get_user_model().EMAIL_FIELD
    except:
        email_field = 'email'

    return email_field


class JSONWebTokenSerializer(Serializer):
    """
    Serializer class used to validate a email and password.

    Returns a JSON Web Token that can be used to authenticate later calls.
    """
    def __init__(self, *args, **kwargs):
        """
        Dynamically add the EMAIL_FIELD to self.fields.
        """
        super(JSONWebTokenSerializer, self).__init__(*args, **kwargs)

        self.fields[self.email_field] = serializers.CharField()
        self.fields['password'] = PasswordField(write_only=True)

    @property
    def email_field(self):
        return get_email_field()

    def validate(self, attrs):
        credentials = {
            self.email_field: attrs.get(self.email_field),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{email_field}" and "password".')
            msg = msg.format(email_field=self.email_field)
            raise serializers.ValidationError(msg)

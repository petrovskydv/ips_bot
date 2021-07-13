from rest_framework import serializers
from phonenumber_field.validators import validate_international_phonenumber
from django.core.validators import validate_email

from api.services import normalize_phonenumber


class CustomerSerializer(serializers.Serializer):
    credential_type = serializers.CharField(required=True, allow_blank=False)
    credential = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(required=False, allow_blank=True)
    tg_chat_id = serializers.IntegerField(required=True)

    def validate(self, data):
        cred_type = data['credential_type']
        cred = data['credential']
        pw = data['password']
        if cred_type == 'phonenumber':
            cred = normalize_phonenumber(cred)
            validate_international_phonenumber(cred)
            data['credential'] = cred
        if cred_type == 'email':
            if cred == '' or cred == ' ':
                raise serializers.ValidationError('Пустой имеил')
            validate_email(cred)
        if cred_type == 'login':
            if pw == '' or pw == ' ':
                raise serializers.ValidationError('Пустой пароль')
        return data


class TariffSerializer(serializers.Serializer):
    # dead brunch
    new_tariff_link_id = serializers.IntegerField(required=True)
    tg_chat_id = serializers.IntegerField(required=True)

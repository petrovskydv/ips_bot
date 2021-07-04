from rest_framework import serializers
from phonenumber_field.validators import validate_international_phonenumber
from django.core.validators import validate_email

from api.services import normalize_phonenumber
from content.models import Customer


class CustomerSerializer(serializers.Serializer):
    credential_type = serializers.CharField(required=True, allow_blank=False)
    credential = serializers.CharField(required=True, allow_blank=False)
    tg_chat_id = serializers.IntegerField(required=True)

    def validate(self, data):
        cred_type = data['credential_type']
        cred = data['credential']
        tg_chat_id = data['tg_chat_id']
        if cred_type == 'phonenumber':
            cred = normalize_phonenumber(cred)
            validate_international_phonenumber(cred)
            data['credential'] = cred
        if cred_type == 'email':
            if cred == '' or cred == ' ':
                raise serializers.ValidationError('Пустой имеил')
            validate_email(cred)
        if Customer.objects.filter(tg_chat_id=tg_chat_id).count() != 0:
            raise serializers.ValidationError('Пользователь с таким тг чат айди уже существует')
        return data
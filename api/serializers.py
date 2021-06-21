from rest_framework import serializers
from phonenumber_field.validators import validate_international_phonenumber
from django.core.validators import validate_email

from api.services import fix_eight


class CustomerSerializer(serializers.Serializer):
    credential_type = serializers.CharField(required=True, allow_blank=False)
    credential = serializers.CharField(required=True, allow_blank=False)
    tg_chat_id = serializers.IntegerField(required=True)

    def validate(self, data):
        cred_type = data['credential_type']
        cred = data['credential']
        if cred_type == 'phonenumber':
            cred = fix_eight(cred)
            validate_international_phonenumber(cred)
        if cred_type == 'email':
            if cred == '' or cred == ' ':
                raise serializers.ValidationError('Пустой имеил')
            validate_email(cred)
        return data
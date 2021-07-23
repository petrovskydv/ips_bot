from rest_framework import serializers
from phonenumber_field.validators import validate_international_phonenumber
from django.core.validators import validate_email
from datetime import date

from api.services import normalize_phonenumber, normalize_date, parse_date


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


class DateSerializer(serializers.Serializer):
    possible_start_date = serializers.CharField(required=True, allow_blank=False, min_length=6, max_length=50)
    possible_end_date = serializers.CharField(required=True, allow_blank=False, min_length=6, max_length=50)

    def validate(self, data):
        possible_start_date = data['possible_start_date']
        possible_end_date = data['possible_end_date']
        normalized_possible_start_date = normalize_date(possible_start_date)
        normalized_possible_end_date = normalize_date(possible_end_date)
        parsed_start_date = parse_date(normalized_possible_start_date)
        if not parsed_start_date:
            raise serializers.ValidationError('Дата начала не определяется')
        parsed_end_date = parse_date(normalized_possible_end_date)
        if not parsed_end_date:
            raise serializers.ValidationError('Дата окончания не определяется')
        if parsed_end_date <= parsed_start_date:
            raise serializers.ValidationError('Дата окончания не больше даты начала')
        if parsed_start_date < date.today():
            raise serializers.ValidationError('Дата начала определена как прошлое')
        return {'start_date': parsed_start_date, 'end_date': parsed_end_date}

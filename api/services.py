import requests

from content.models import Customer, Tariff
from django.db.models import Q


def fix_eight(num: str) -> str:
    if num.startswith('8'):
        return num.replace('8', '+7')
    return num


def normalize_phonenumber(num: str) -> str:
    num = fix_eight(num)
    for index, character in enumerate(num):
        if character == ' ' or character == '-' or character == '(' or character == ')':
            num.replace(num[index], '', 1)
    return num


def normalize_customer_data(data: dict) -> dict:
    # TODO перенести эту штуку в сериалайзер
    # result = {data['credential_type']: data['credential'], 'tg_chat_id': data['tg_chat_id']}
    # if data['credential_type'] == 'login':
    #     result['password'] = data['password']
    # try:
    #     result['netup_account_id'] = data['account_id']
    # except KeyError:
    #     pass
    data[data['credential_type']] = data['credential']
    return data


def create_customer(data: dict) -> bool:
    # somewhat dead branch
    customer = Customer.objects.create(**data)
    customer.save()
    return True


def update_customer(profile_data: dict, validated_data: dict):
    tariff_netup_ids = [tariff['id'] for tariff in profile_data['tariffs']]
    tariffs = Tariff.objects.filter(netup_tariff_id__in=tariff_netup_ids)
    customer = Customer.objects.get(tg_chat_id=validated_data['tg_chat_id'])
    customer.update(netup_account_id=profile_data['id'])
    customer.add(*tariffs)
    customer.save()
    return True


def get_or_create_customer(data: dict) -> bool:
    _, created = Customer.objects.get_or_create(**data)
    return created


def login_to_netup(validated_data: dict) -> dict:
    login = validated_data['credential']
    password = validated_data['password']
    print(login, password)
    url = 'http://localhost/customer_api/login'
    payload = {
        "login": login,
        "password": password
    }
    response = requests.post(url, payload=payload)
    response.raise_for_status()
    print(response.text())
    is_new_customer = get_or_create_customer(validated_data)
    return {'success': True, 'new_customer': is_new_customer}


def fetch_customer_profile(validated_data, is_new_customer):
    url = 'http://localhost/customer_api/auth/profile'
    response = requests.get(url)
    response.raise_for_status()
    profile_data = response.json()
    if is_new_customer:
        update_customer(profile_data, validated_data)
    # TODO посчитать сколько дней до отключения
    # TODO вывести больше информации о тарифах
    customer_info = {
        'is_active': profile_data['is_active'],
        'balance': profile_data['balance'],
        'tariffs': profile_data['tariffs'],
        'full_name': profile_data['full_name']
    }
    return customer_info


def change_tariff(validated_data):
    customer = Customer.objects.get(tg_chat_id=validated_data['tg_chat_id'])

    url = 'http://localhost/customer_api/auth/tariffs'
    # TODO сделать нормальное получение нетапп линк айди
    payload = {
        "tariff_link_id": customer.tariffs.filter(main=True).netup_tariff_link_id,
        "account_id": customer.netup_account_id,
        "next_tariff_id": validated_data['new_tariff_link_id'],
    }
    response = requests.get(url, payload=payload)
    response.raise_for_status()
    return True if response['result'] == 'OK' else False

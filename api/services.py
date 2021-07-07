import requests
import json

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
    data[data['credential_type']] = data['credential']
    data.pop('credential_type', None)
    data.pop('credential', None)
    return data


def normalize_tariffs(tariffs: dict) -> dict:
    for tariff in tariffs:
        tariff['netup_tariff_id'] = tariff['id']
        tariff.pop('id', None)
        tariff['title'] = tariff['name']
        tariff.pop('name', None)
        tariff['netup_tariff_link_id'] = tariff['tariff_link_id']
        tariff.pop('tariff_link_id', None)
    return tariffs

def create_customer(data: dict) -> bool:
    # somewhat dead branch
    # customer = Customer.objects.create(**data)
    # customer.save()
    return True


def update_customer(tg_chat_id: str, tariffs: dict):
    # TODO сделать комманду заполняющую бд тарифы
    # tariff_netup_ids = [tariff['id'] for tariff in tariffs']
    # tariffs = Tariff.objects.filter(netup_tariff_id__in=tariff_netup_ids)

    customer = Customer.objects.get(tg_chat_id=tg_chat_id)
    customer.update(netup_account_id=profile_data['id'])
    customer.add(*tariffs)
    customer.save()
    return True


def get_or_create_customer(data: dict) -> bool:
    _, created = Customer.objects.get_or_create(**data)
    return created


def login_to_netup(normalized_data: dict) -> dict:
    login = normalized_data['login']
    password = normalized_data['password']
    url = 'http://46.101.245.26:1488/customer_api/login'
    credentials = json.dumps({
        "login": login,
        "password": password
    })
    session = requests.session()
    response = session.post(url, data=credentials)
    response.raise_for_status()
    cookies = session.cookies
    sid_customer = cookies.items()[0][1]
    normalized_data['netup_sid'] = sid_customer
    print(normalized_data)
    get_or_create_customer(normalized_data)
    return {'success': True}


def fetch_customer_profile(tg_chat_id):
    customer = Customer.objects.get(tg_chat_id=tg_chat_id)
    url = 'http://46.101.245.26:1488/customer_api/auth/profile'
    session = requests.session()
    session.cookies.update([('sid_customer', customer.netup_sid)])
    response = session.get(url)
    response.raise_for_status()
    profile_data = response.json()
    print('profiledata ', profile_data)

    tariffs = normalize_tariffs(profile_data['tariffs'])
    netup_account_id = profile_data['id']
    is_new_profile = customer.netup_account_id == ''
    print('eto tarify ', tariffs)
    if is_new_profile:
        update_customer(tg_chat_id, {'netup_account_id': netup_account_id, 'tariffs': tariffs})
    # TODO посчитать сколько дней до отключения
    # TODO вывести больше информации о тарифах
    # customer_info = {
    #     'is_active': profile_data['is_active'],
    #     'balance': profile_data['balance'],
    #     'tariffs': profile_data['tariffs'],
    #     'full_name': profile_data['full_name']
    # }
    return True


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


def fetch_tariffs():
    tariffs = Tariff.objects.all()
    tariffs_info = []
    for tariff in tariffs:
        tariff_info = {
            'id': tariff.netup_tariff_id,
            'name': tariff.title,
            'comments': tariff.description,
            'cost': tariff.cost,
        }
        tariffs_info.append(tariff_info)
    return tariffs_info

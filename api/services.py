import requests
import json
import uuid

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


def update_customer(tg_chat_id: str, profile_data: dict):
    # TODO сделать manage-комманду заполняющую бд тарифы
    customer = Customer.objects.get(tg_chat_id=tg_chat_id)
    customer.netup_account_id = profile_data['netup_account_id']
    customer.save()
    TariffRelation = Customer.tariffs.through
    relations = []
    for tariff in profile_data['tariffs']:
        tariff, _ = Tariff.objects.get_or_create(**tariff)
        relations.append(TariffRelation(id=uuid.uuid4(), customer_id=customer, tariff_id=tariff))
    TariffRelation.objects.bulk_create(relations, len(relations))
    print('eto tarify kustomera', customer.tariffs)
    return True


def identify_customer(data: dict) -> bool:
    customer, created = Customer.objects.get_or_create(data['tg_chat_id'])
    if not created:
        if data['password'] == customer.password and data['login'] == customer.login:
            customer.netup_sid = data['netup_sid']
            customer.save()
            return True
        else:
            return False
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
    is_identified = identify_customer(normalized_data)
    return {'success': is_identified}


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

import requests
import json
import uuid

from content.models import Customer, Tariff
from django.core.exceptions import ObjectDoesNotExist
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


def rewrite_customer_tariffs(customer, tariffs):
    # TODO тариф обновился и пользователь на него перешел, но в базе все ещё старый
    customer.tariffs.all().delete()
    TariffRelation = Customer.tariffs.through
    relations = []
    for tariff in tariffs:
        tariff, _ = Tariff.objects.get_or_create(**tariff)
        relations.append(TariffRelation(id=uuid.uuid4(), customer_id=customer, tariff_id=tariff))
    TariffRelation.objects.bulk_create(relations, len(relations))


def update_customer(customer, profile_data: dict):
    # TODO сделать manage-комманду заполняющую бд тарифы
    customer.netup_account_id = profile_data['netup_account_id']
    customer.save()
    recorded_customer_tariffs_ids = list(customer.tariffs.values_list('netup_tariff_id', flat=True))
    fetched_tariffs_ids = [tariff['netup_tariff_id'] for tariff in profile_data['tariffs']]

    for tariff_id in fetched_tariffs_ids:
        if tariff_id not in recorded_customer_tariffs_ids:
            rewrite_customer_tariffs(customer, profile_data['tariffs'])
            break
    print(customer.tariffs.all())
    return True


def identify_customer(data: dict) -> bool:
    try:
        customer = Customer.objects.get(tg_chat_id=data['tg_chat_id'])
        if data['password'] == customer.password and data['login'] == customer.login:
            customer.netup_sid = data['netup_sid']
            customer.save()
            return True
        else:
            return False
    except ObjectDoesNotExist:
        Customer.objects.create(**data)
        return True


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

    tariffs = normalize_tariffs(profile_data['tariffs'])
    netup_account_id = profile_data['id']
    update_customer(customer, {'netup_account_id': netup_account_id, 'tariffs': tariffs})
    # TODO посчитать сколько дней до отключения
    # TODO вывести больше информации о тарифах
    customer_info = {
        'is_active': profile_data['is_active'],
        'balance': profile_data['balance'],
        'tariffs': profile_data['tariffs'],
        'full_name': profile_data['full_name']
    }
    return customer_info


def change_tariff(tg_chat_id, new_tariff_id, old_tariff_id):
    customer = Customer.objects.get(tg_chat_id=tg_chat_id)

    url = 'http://46.101.245.26:1488/customer_api/auth/tariffs'
    payload = json.dumps({
        "tariff_link_id": int(customer.tariffs.get(netup_tariff_id=old_tariff_id).netup_tariff_link_id),
        "account_id": int(customer.netup_account_id),
        "next_tariff_id": new_tariff_id
    })
    session = requests.session()
    session.cookies.update([('sid_customer', customer.netup_sid)])
    response = session.post(url, data=payload)
    response.raise_for_status()
    unpucked_response = response.json()
    print(unpucked_response)
    return True


def fetch_tariffs(tg_chat_id: int) -> dict:
    customer = Customer.objects.get(tg_chat_id=tg_chat_id)
    recorded_customer_tariffs_ids = list(customer.tariffs.values_list('netup_tariff_id', flat=True))

    session = requests.session()
    session.cookies.update([('sid_customer', customer.netup_sid)])
    url = 'http://46.101.245.26:1488/customer_api/auth/tariffs'
    response = session.get(url)
    response.raise_for_status()
    all_tariffs = response.json()

    for tariff in all_tariffs:
        tariff['activated'] = False
        if tariff['id'] in recorded_customer_tariffs_ids:
            tariff['name'] = f"[Подключён] {tariff['name']}"
            tariff['activated'] = True

    return all_tariffs


def fetch_tariff_info(tg_chat_id: int, tariff_id: int) -> dict:
    customer = Customer.objects.get(tg_chat_id=tg_chat_id)
    session = requests.session()
    session.cookies.update([('sid_customer', customer.netup_sid)])
    url = 'http://46.101.245.26:1488/customer_api/auth/tariffs'
    response = session.get(url)
    response.raise_for_status()
    all_tariffs = response.json()
    for tariff in all_tariffs:
        if tariff['id'] == tariff_id:
            return tariff
    return {}

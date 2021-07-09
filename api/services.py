import requests
import json
import uuid
import copy

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
        try:
            tariff['netup_tariff_link_id'] = tariff['tariff_link_id']
            tariff.pop('tariff_link_id', None)
        except KeyError:
            pass
        try:
            tariff['description'] = tariff['comments']
            tariff.pop('comment', None)
        except KeyError:
            pass
    return tariffs


def create_customer(data: dict) -> bool:
    # somewhat dead branch
    # customer = Customer.objects.create(**data)
    # customer.save()
    return True


def rewrite_customer_tariffs(customer, tariffs):
    # TODO тариф обновился и пользователь на него перешел, но в базе все ещё старый
    # TODO bulk_create слишком пафосно
    customer.subscription_set.all().delete()
    Subscription = Customer.tariffs.through
    relations = []
    for tariff in tariffs:
        link_id = tariff.pop('netup_tariff_link_id')
        try:
            tariff = Tariff.objects.get(netup_tariff_id=tariff['netup_tariff_id'])
        except ObjectDoesNotExist:
            tariff = Tariff.objects.create(**tariff)
        relations.append(Subscription(id=uuid.uuid4(), customer_id=customer, tariff_id=tariff, link_id=link_id))
    Subscription.objects.bulk_create(relations, len(relations))


def change_tariff_relation(customer, new_tariff_id: int, old_tariff_id: int):
    # TODO вроде, линк айди не меняется от смены тарифа, но потом надо добавить проверку
    old_tariff = Tariff.objects.get(netup_tariff_id=old_tariff_id)
    new_tariff = Tariff.objects.get(netup_tariff_id=new_tariff_id)
    Subscription = Customer.tariffs.through
    relation = Subscription.objects.get(customer_id=customer, tariff_id=old_tariff)
    relation.tariff_id = new_tariff
    relation.save()
    return True


def update_customer(customer, profile_data: dict):
    customer.netup_account_id = profile_data['netup_account_id']
    customer.save()
    fetched_tariffs_ids = [tariff['netup_tariff_id'] for tariff in profile_data['tariffs']]
    recorded_customer_tariffs_ids = list(customer.tariffs.values_list('netup_tariff_id', flat=True))

    for tariff_id in fetched_tariffs_ids:
        if tariff_id not in recorded_customer_tariffs_ids:
            rewrite_customer_tariffs(customer, profile_data['tariffs'])
            break
    print(customer.tariffs.all())
    return True


def fetch_change_status(tg_chat_id) -> dict:
    # TODO полубому формирования словаря можно сделать красивее
    customer = Customer.objects.get(tg_chat_id=tg_chat_id)
    session = requests.session()
    session.cookies.update([('sid_customer', customer.netup_sid)])
    url = 'http://46.101.245.26:1488/customer_api/auth/switchtariffsettings'
    response = session.get(url)
    response.raise_for_status()
    tariff_change_status = {}
    for tariff_group in response.json():
        change_status = tariff_group['instant_change']
        tariff_ids = [tariff['tariff_id'] for tariff in tariff_group['data']]
        for tariff_id in tariff_ids:
            tariff_change_status[tariff_id] = change_status
    return tariff_change_status


def update_tariffs(tariffs, tg_chat_id):
    change_status = fetch_change_status(tg_chat_id)
    for tariff in tariffs:
        recorded_tariff, created = Tariff.objects.get_or_create(netup_tariff_id=tariff['netup_tariff_id'])
        recorded_tariff.title = tariff['title']
        try:
            recorded_tariff.description = tariff['description']
        except KeyError:
            pass
        recorded_tariff.cost = tariff['cost']
        recorded_tariff.tariff_type = 'TV' if 'ТВ' in tariff['title'] else 'IN'
        recorded_tariff.instant_change = change_status[tariff['netup_tariff_id']]
        recorded_tariff.save()


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
    link_id = customer.subscription_set.get(
        customer_id=customer,
        tariff_id=customer.tariffs.get(netup_tariff_id=old_tariff_id)
    ).link_id
    payload = json.dumps({
        "tariff_link_id": int(link_id),
        "account_id": int(customer.netup_account_id),
        "next_tariff_id": new_tariff_id
    })
    session = requests.session()
    session.cookies.update([('sid_customer', customer.netup_sid)])
    response = session.post(url, data=payload)
    response.raise_for_status()
    unpucked_response = response.json()
    if unpucked_response:
        change_tariff_relation(customer, new_tariff_id, old_tariff_id)
    return unpucked_response['result'] == 'OK'


def fetch_tariffs(tg_chat_id: int) -> dict:
    customer = Customer.objects.get(tg_chat_id=tg_chat_id)
    recorded_customer_tariffs_ids = list(customer.tariffs.values_list('netup_tariff_id', flat=True))

    session = requests.session()
    session.cookies.update([('sid_customer', customer.netup_sid)])
    url = 'http://46.101.245.26:1488/customer_api/auth/tariffs'
    response = session.get(url)
    response.raise_for_status()
    all_tariffs = response.json()
    normalized_tariffs = normalize_tariffs(copy.deepcopy(all_tariffs))
    update_tariffs(normalized_tariffs, tg_chat_id)

    # TODO избавить фронт от этого формата тарифов
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


def fetch_available_tariffs_info(tg_chat_id: int, tariff_id: int):
    # TODO Когда поменяется формат тарифов на фронте можно тут поменять всё и убрать дубли кода от DRYить так сказать
    # TODO убрать миллиард запросов к бд!
    tariff = Tariff.objects.get(netup_tariff_id=tariff_id)
    tariff_type = tariff.tariff_type
    available_tariffs = Tariff.objects.filter(tariff_type=tariff_type).all().exclude(pk=tariff.pk)
    available_tariffs_ids = list(available_tariffs.values_list('netup_tariff_id', flat=True))
    customer = Customer.objects.get(tg_chat_id=tg_chat_id)

    session = requests.session()
    session.cookies.update([('sid_customer', customer.netup_sid)])
    url = 'http://46.101.245.26:1488/customer_api/auth/tariffs'
    response = session.get(url)
    response.raise_for_status()
    all_tariffs = response.json()
    available_tariffs = []
    for tariff in all_tariffs:
        if tariff['id'] in available_tariffs_ids:
            recodred_tariff = Tariff.objects.get(pk=tariff['id'])
            tariff['instant_change'] = recodred_tariff.instant_change
            available_tariffs.append(tariff)
    return available_tariffs

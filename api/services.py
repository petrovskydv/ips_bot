from contextlib import suppress
from datetime import datetime
from dateutil import parser
from dateutil.parser._parser import ParserError
from datetime import datetime, date

import time
import requests
import json
import uuid
import copy

from config.settings import NETUP_URL
from content.models import Customer, Tariff
from django.core.exceptions import ObjectDoesNotExist


def fix_eight(phone_number: str) -> str:
    if phone_number.startswith('8'):
        return phone_number.replace('8', '+7')
    return phone_number


def normalize_date(possible_date: str) -> str:
    chars_to_replace = """_()-.\,"""
    for character in possible_date:
        if character in chars_to_replace:
            possible_date = possible_date.replace(character, ' ')
    return possible_date


def normalize_phonenumber(phone_number: str) -> str:
    phone_number = fix_eight(phone_number)
    unnecessary_characters = '- ()'
    return ''.join(list(filter(lambda c: c not in unnecessary_characters, phone_number)))


def make_session_customer(tg_chat_id):
    customer = Customer.objects.get(tg_chat_id=tg_chat_id)
    session = requests.session()
    session.cookies.update([('sid_customer', customer.netup_sid)])
    return session, customer


def normalize_customer_data(data: dict) -> dict:
    data[data['credential_type']] = data['credential']
    data.pop('credential_type', None)
    data.pop('credential', None)
    return data


def normalize_tariffs(tariffs: dict) -> dict:
    for tariff in tariffs:
        with suppress(KeyError):
            tariff['netup_tariff_id'] = tariff['id']
            tariff.pop('id', None)

            tariff['title'] = tariff['name']
            tariff.pop('name', None)

            tariff['netup_tariff_link_id'] = tariff['tariff_link_id']
            tariff.pop('tariff_link_id', None)

            tariff['description'] = tariff['comments']
            tariff.pop('comments', None)

    return tariffs


def parse_date(possible_date):
    try:
        return parser.parse(possible_date).date()
    except ParserError:
        return None


def rewrite_customer_tariffs(customer, tariffs):
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
    return True


def fetch_change_status(session) -> dict:
    url = f'{NETUP_URL}/customer_api/auth/switchtariffsettings'
    response = session.get(url)
    response.raise_for_status()
    tariff_change_status = {}
    for tariff_group in response.json():
        change_status = tariff_group['instant_change']
        tariff_ids = [tariff['tariff_id'] for tariff in tariff_group['data']]
        for tariff_id in tariff_ids:
            tariff_change_status[tariff_id] = change_status
    return tariff_change_status


def update_tariffs(tariffs, session):
    change_status = fetch_change_status(session)
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
    url = f'{NETUP_URL}/customer_api/login'
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
    is_identified = identify_customer(normalized_data)
    return {'success': is_identified}


def logout_from_netup(tg_chat_id):
    customer = Customer.objects.get(tg_chat_id=tg_chat_id)
    # TODO кажись это строчка теперь не нужна
    customer.subscription_set.all().delete()
    customer.delete()
    return {'success': True}


def fetch_customer_profile(tg_chat_id):
    session, customer = make_session_customer(tg_chat_id)
    url = f'{NETUP_URL}/customer_api/auth/profile'
    response = session.get(url)
    response.raise_for_status()
    profile_data = response.json()

    tariffs = normalize_tariffs(profile_data['tariffs'])
    netup_account_id = profile_data['id']
    update_customer(customer, {'netup_account_id': netup_account_id, 'tariffs': tariffs})

    recommended_payment = profile_data['payment_in_month'] - profile_data['balance']
    if recommended_payment <= 0:
        recommended_payment = 0
    customer_info = {
        'is_active': profile_data['is_active'],
        'balance': profile_data['balance'],
        'tariffs': profile_data['tariffs'],
        'credit': profile_data['credit'],
        'payment_in_month': profile_data['payment_in_month'],
        'full_name': profile_data['full_name'],
        'recommended_payment': recommended_payment
    }
    return customer_info


def change_tariff(tg_chat_id, new_tariff_id, old_tariff_id):
    session, customer = make_session_customer(tg_chat_id)

    url = f'{NETUP_URL}/customer_api/auth/tariffs'
    link_id = customer.subscription_set.get(
        customer_id=customer,
        tariff_id=customer.tariffs.get(netup_tariff_id=old_tariff_id)
    ).link_id
    payload = json.dumps({
        "tariff_link_id": int(link_id),
        "account_id": int(customer.netup_account_id),
        "next_tariff_id": new_tariff_id
    })
    response = session.post(url, data=payload)
    response.raise_for_status()
    unpucked_response = response.json()
    if unpucked_response:
        change_tariff_relation(customer, new_tariff_id, old_tariff_id)
    return unpucked_response['result'] == 'OK'


def fetch_tariffs(tg_chat_id: int) -> dict:
    session, customer = make_session_customer(tg_chat_id)
    recorded_customer_tariffs_ids = list(customer.tariffs.values_list('netup_tariff_id', flat=True))
    url = f'{NETUP_URL}/customer_api/auth/tariffs'
    response = session.get(url)
    response.raise_for_status()
    all_tariffs = response.json()
    normalized_tariffs = normalize_tariffs(copy.deepcopy(all_tariffs))
    update_tariffs(normalized_tariffs, session)

    for tariff in normalized_tariffs:
        tariff['activated'] = False
        if tariff['netup_tariff_id'] in recorded_customer_tariffs_ids:
            tariff['title'] = f"[Подключён] {tariff['title']}"
            tariff['activated'] = True

    return normalized_tariffs


def fetch_tariff_info(tg_chat_id: int, tariff_id: int) -> dict:
    session, customer = make_session_customer(tg_chat_id)
    url = f'{NETUP_URL}/customer_api/auth/tariffs'
    response = session.get(url)
    response.raise_for_status()
    normalized_tariffs = normalize_tariffs(response.json())
    for tariff in normalized_tariffs:
        if tariff['netup_tariff_id'] == tariff_id:
            return tariff
    return {}


def fetch_available_tariffs_info(tariff_id: int):
    tariff = Tariff.objects.get(netup_tariff_id=tariff_id)
    tariff_type = tariff.tariff_type
    available_tariffs = Tariff.objects.filter(tariff_type=tariff_type).all().exclude(pk=tariff.pk).values()

    return available_tariffs


def connect_tariff(tg_chat_id: int, tariff_id: int):
    session, customer = make_session_customer(tg_chat_id)
    url = f'{NETUP_URL}/customer_api/auth/independent_connect_services'
    payload = json.dumps({
        "account_id": int(customer.netup_account_id),
        "setting_id": tariff_id
    })
    response = session.post(url, data=payload)
    response.raise_for_status()
    unpucked_response = response.json()
    return unpucked_response['result'] == 'OK'


def make_promised_payment(tg_chat_id: int, value: int):
    session, customer = make_session_customer(tg_chat_id)

    url = f'{NETUP_URL}/customer_api/auth/promisedpaymentsettings'
    response = session.get(url)
    unpucked_response = response.json()
    max_value = unpucked_response['max_value']
    min_balance = unpucked_response['min_balance']

    url = f'{NETUP_URL}/customer_api/auth/profile'
    response = session.get(url)
    response.raise_for_status()
    balance = response.json()['balance']

    if value > max_value or balance < min_balance:
        return False

    url = f'{NETUP_URL}/customer_api/auth/promisedpayment'
    payload = json.dumps({
        "account_id": int(customer.netup_account_id),
        "value": value
    })
    response = session.post(url, data=payload)
    response.raise_for_status()
    unpucked_response = response.json()
    return unpucked_response['result'] == 'OK'


def fetch_promised_payment_status(tg_chat_id: int):
    session, customer = make_session_customer(tg_chat_id)

    url = f'{NETUP_URL}/customer_api/auth/promisedpaymentsettings'
    response = session.get(url)
    unpucked_response = response.json()
    max_value = unpucked_response['max_value']
    min_balance = unpucked_response['min_balance']
    is_enabled = unpucked_response['is_enabled'] == 1

    url = f'{NETUP_URL}/customer_api/auth/profile'
    response = session.get(url)
    response.raise_for_status()
    balance = response.json()['balance']

    return {
        'balance_allowed': balance > min_balance,
        'is_enabled': is_enabled,
        'max_value': max_value
    }


def fetch_payment_history(tg_chat_id: int):
    session, customer = make_session_customer(tg_chat_id)
    url = f'{NETUP_URL}/customer_api/auth/full_statistics'
    params = {'range': 12}
    response = session.get(url, params=params)
    response.raise_for_status()
    payments = response.json()
    return convert_payments(payments)


def convert_payments(payments):
    payment_types_compliance = {
        'Card payment': 'Платеж картой',
        'Credit': 'Кредит',
        'Cash payment': 'Платеж наличными',
        'Wire transfer': 'Перевод средств',
    }
    converted_payments = []
    for payment in payments:
        if not payment['event_name'] in payment_types_compliance:
            continue
        converted_payments.append({
            'event_name': payment_types_compliance[payment['event_name']],
            'actual_date': datetime.utcfromtimestamp(payment['actual_date']).strftime('%d.%m.%Y %H:%M'),
            'payment_incurrency': payment['payment_incurrency'],
        })
    return converted_payments


def set_suspend(tg_chat_id, data):
    session, customer = make_session_customer(tg_chat_id)
    url = 'http://46.101.245.26:1488/customer_api/auth/enablesuspend'
    start_timestamp = int(time.mktime(datetime.strptime(str(data['start_date']), "%Y-%m-%d").timetuple()))
    end_timestamp = int(time.mktime(datetime.strptime(str(data['end_date']), "%Y-%m-%d").timetuple()))
    payload = json.dumps({
        "account_id": int(customer.netup_account_id),
        "start": start_timestamp,
        "end": end_timestamp
    })
    response = session.post(url, data=payload)
    response.raise_for_status()
    try:
        unpucked_response = response.json()
    except json.JSONDecodeError:
        unpucked_response = {'result': 'NOT OK'}
    return unpucked_response['result'] == 'OK'


def fetch_suspension_settings(tg_chat_id):
    session, customer = make_session_customer(tg_chat_id)
    url = 'http://46.101.245.26:1488/customer_api/auth/voluntarysuspensionsettings'
    response = session.get(url, params={'account_id': int(customer.netup_account_id)})
    response.raise_for_status()
    unpucked_response = response.json()
    block_start = datetime.utcfromtimestamp(int(unpucked_response['block_start'])).strftime('%Y-%m-%d')
    block_end = datetime.utcfromtimestamp(int(unpucked_response['block_end'])).strftime('%Y-%m-%d')
    if unpucked_response['is_blocked']:
        return {
            'is_blocked': True,
            'blocked_now': parse_date(block_start) <= date.today(),
            'block_start': block_start,
            'block_end': block_end
        }
    return {'is_blocked': False}


def disable_suspension(tg_chat_id):
    session, customer = make_session_customer(tg_chat_id)
    url = 'http://46.101.245.26:1488/customer_api/auth/disablesuspend'
    payload = json.dumps({
        "account_id": int(customer.netup_account_id)
    })
    response = session.post(url, data=payload)
    response.raise_for_status()
    try:
        unpucked_response = response.json()
    except json.JSONDecodeError:
        unpucked_response = {'result': 'NOT OK'}
    return unpucked_response['result'] == 'OK'

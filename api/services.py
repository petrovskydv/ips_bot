from content.models import Customer


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


def customer_dict_factory(data: dict) -> dict:
    result = {data['credential_type']: data['credential'], 'tg_chat_id': data['tg_chat_id']}
    return result


def create_customer(data: dict) -> bool:
    customer_data = customer_dict_factory(data)
    customer = Customer.objects.create(**customer_data)
    customer.save()
    return True


def update_customer(data: dict) -> bool:
    customer_data = customer_dict_factory(data)
    customer = Customer.objects.get(tg_chat_id=customer_data['tg_chat_id'])
    customer.update(**customer_data)
    customer.save()

    return True

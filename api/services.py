from content.models import Customer


def fix_eight(num):
    if num.startswith('8'):
        return num.replace('8', '+7')
    return num


def create_customer(data):
    res = {}
    cred_type = data['credential_type']
    cred = data['credential']
    res[cred_type] = cred
    res['tg_chat_id'] = data['tg_chat_id']
    customer = Customer.objects.create(**res)
    customer.save()
    return True


def update_customer(data):
    res = {}
    cred_type = data['credential_type']
    cred = data['credential']
    res[cred_type] = cred
    tg_chat_id = data['tg_chat_id']

    customer = Customer.objects.get(tg_chat_id=tg_chat_id)
    customer.update(**res)
    customer.save()

    return True

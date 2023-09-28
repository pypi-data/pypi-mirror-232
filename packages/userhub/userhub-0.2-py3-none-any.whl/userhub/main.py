"""
Functionality of authorization
"""

import re
import requests


LINK = 'https://chill.services/api/account/proj/'


def check_phone(cont):
    """ Phone checking """
    return 11 <= len(str(cont)) <= 18

def pre_process_phone(cont):
    """ Phone number pre-processing """

    if not cont:
        return 0

    cont = str(cont)

    if cont[0] == '8':
        cont = '7' + cont[1:]

    cont = re.sub(r'[^0-9]', '', cont)

    if not cont:
        return 0

    return int(cont)

def check_mail(cont):
    """ Mail checking """
    return re.match(r'.+@.+\..+', cont) is not None


def detect_type(login):
    """ Detect the type of authorization """

    if check_phone(pre_process_phone(login)):
        return 'phone'

    if check_mail(login):
        return 'mail'

    return 'login'

def auth(
    request: dict,
    data: dict,
    by: str,
    online: bool = False,
    password: bool = False,
    image: str = None,
):
    """ Auth """

    res = requests.post(LINK, json={
        'request': request,
        'data': data,
        'by': by,
        'online': online,
        'password': password,
        'image': image,
    }).json()

    return res['user'], res['token'], res['new']

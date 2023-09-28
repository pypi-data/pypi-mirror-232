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
    by: str,
    token: str,
    network: int = 0,
    ip: str = None,
    locale: str = 'en',
    project: str = None,
    login: str = None,
    social: int = None,
    user: str = None,
    password: str = None,
    name: str = None,
    surname: str = None,
    image: str = None,
    mail: str = None,
    utm: str = None,
    online: bool = False,
    check_password: bool = False,
):
    """ Auth """

    req = {
        'by': by,
        'token': token,
        'network': network,
        'ip': ip,
        'locale': locale,
        'project': project,
        'login': login,
        'social': social,
        'user': user,
        'password': password,
        'name': name,
        'surname': surname,
        'image': image,
        'mail': mail,
        'utm': utm,
        'online': online,
        'check_password': check_password,
    }

    res = requests.post(LINK, json=req).json()
    return res['user'], res['token'], res['new']

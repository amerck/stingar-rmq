import json
import string
import uuid
from random import choice
from datetime import datetime


class RegistrationEvent:

    def __init__(self):
        pass

    @staticmethod
    def rand_str(n):
        el = string.ascii_letters + string.digits
        return ''.join(choice(el) for _ in range(n))

    def normalize(self, data):
        uid = str(uuid.uuid4())
        created_date = datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S.%f")
        secret = self.rand_str(16)

        reg_dict = json.loads(data)
        registration = {
            'name': reg_dict['name'],
            'hostname': reg_dict['hostname'],
            'ip': reg_dict['ip'],
            'honeypot': reg_dict['honeypot'],
            'uuid': uid,
            'created_date': created_date,
            'identifier': uid,
            'publish': ['cowrie.sessions'],
            'secret': secret
        }
        return registration


class RawEvent:

    def __init__(self):
        pass

    @staticmethod
    def normalize(channel, uid, data):
        payload = json.loads(data)
        raw_event = {
            "ident": uid,
            "timestamp": datetime.utcnow(),
            "channel": channel,
            "payload": payload
        }
        return raw_event

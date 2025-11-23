# -*- coding: utf-8 -*-
""" UniBasic Markup Language """

import pickle
import hashlib
from typing import Any


HEADER = 'SECPICKLE'


class HashCheckFailed(Exception):
    """ Error for failing the hash check """


def _secure_dumps(data: Any) -> bytes:
    """ Scure pickle.dumps """
    bin_data: bytes = pickle.dumps(data)
    hashed: str = hashlib.sha256(bin_data).hexdigest()
    header: bytes = f"{HEADER}{hashed}".encode("utf-8")
    dump_data: bytes = header + b'\n' + bin_data
    return dump_data


def _secure_loads(data: bytes) -> Any:
    """ Secure pickle.loads """
    header, body = data.split(b'\n', maxsplit=1)
    meta: str = header.decode('utf-8')
    meta_hash: str = meta[len(HEADER):]\
        if meta.startswith(HEADER) else ''
    if meta_hash != hashlib.sha256(body).hexdigest():
        raise HashCheckFailed('mismatching hashes for '
                              'the pickle object')
    return pickle.loads(body)


class UBML:
    pass


class UBMLB(UBML):
    pass

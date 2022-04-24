from functools import wraps
from flask import request, session
from sklearn.ensemble import RandomForestClassifier
from hashlib import md5
from time import time
from datetime import datetime


def get_row():
    header_keys = sorted(list(request.headers.keys()))
    header_hash = md5(' '.join(header_keys).encode('ascii')).hexdigest()

    if 'last_req_at' in session:
        time_since_last_req = time() - session.get('last_req_at')
    else:
        time_since_last_req = 0

    session['last_req_at'] = time()

    parts = (
        request.remote_addr,
        session['id'],
        datetime.now().strftime("%Y-%m-%d:%H:%M:%S"),
        request.method,
        request.path,
        request.user_agent.string,
        str(header_hash),
        f"{time_since_last_req*1000:.4f}",
    )

    return ','.join(parts)


def protected_endpoint(function):
    """

    :param function:
    :return:
    """

    @wraps(function)
    def wrapper():
        blocked = False

        # TODO implement ML model
        print(get_row())

        return function(blocked)

    return wrapper

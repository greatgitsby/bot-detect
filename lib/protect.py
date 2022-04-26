from functools import wraps

from flask import request

from lib.dataset_collector import get_request_log
from lib.dataset_processor import get_session_stats_for_ip

def protected_endpoint(function):
    """

    :param function:
    :return:
    """

    @wraps(function)
    def wrapper():
        blocked = False
        ip = request.remote_addr

        if 'X-Fake-Remote-Ip' in request.headers:
            ip = request.headers.get('x-fake-remote-ip')

        request_log = get_request_log()

        if len(request_log) > 0:
            session_X = get_session_stats_for_ip(request_log, ip).to_numpy()
            print(session_X)

            # TODO implement ML model

        return function(blocked)

    return wrapper

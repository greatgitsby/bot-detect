from functools import wraps
from flask import request


def protected_endpoint(function):
    """

    :param function:
    :return:
    """

    @wraps(function)
    def wrapper():
        url = request.url
        print(f"Protecting {url}")
        blocked = "product" in url

        return function(blocked)

    return wrapper

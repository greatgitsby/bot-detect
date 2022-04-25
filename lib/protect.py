from functools import wraps


def protected_endpoint(function):
    """

    :param function:
    :return:
    """

    @wraps(function)
    def wrapper():
        blocked = False

        # TODO implement ML model

        return function(blocked)

    return wrapper

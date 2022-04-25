from flask import request, session, Response, g
from hashlib import md5
from datetime import datetime
import uuid
import pandas as pd

from dataset_preprocessor import process

__DONT_USE_DATAFRAME: pd.DataFrame | None = None


def get_request_attrs() -> dict:
    """
    Get the row for the dataset

    (
        IP,
        Session ID,
        Current time,
        HTTP Method,
        HTTP Path,
        HTTP User Agent,
        A hash of the HTTP headers (keys) - ordering and case are important,
        Time since last request
    )

    :return:
    """

    ip = request.remote_addr
    header_keys = sorted(list(request.headers.keys()))

    if 'X-Fake-Remote-Ip' in header_keys:
        ip = request.headers.get('x-fake-remote-ip')
        header_keys.remove('X-Fake-Remote-Ip')

    print(header_keys)

    header_hash = md5(' '.join(header_keys).encode('ascii')).hexdigest()

    if 'id' not in session:
        session['id'] = str(uuid.uuid4())

    return {
        'ip': ip,
        'sess_id': str(session['id']),
        'time': pd.Timestamp(ts_input=datetime.now().isoformat()),
        'req_method': request.method,
        'req_path': request.path,
        'req_depth': request.path.count("/"),
        'ua': request.user_agent.string,
        'referer': request.referrer,
        'header_hash': str(header_hash),
    }


def get_response_attrs(response: Response) -> dict:
    return {
        'resp_code': response.status_code,
        'resp_content_type': response.content_type,
        'resp_content_length': response.content_length,
    }


def data_collector_request_handler(*args, **kwargs):
    if g and '__request_attrs__' not in g:
        g.__request_attrs__ = get_request_attrs()


def data_collector_response_handler(response: Response):
    global __DONT_USE_DATAFRAME

    if g and '__request_attrs__' in g:
        entry = {}

        request_log_entry = dict(g.__request_attrs__)
        response_log_entry = dict(get_response_attrs(response))

        entry.update(request_log_entry)
        entry.update(response_log_entry)

        for k in entry.keys():
            entry[k] = [entry[k]]

        pd_entry = pd.DataFrame.from_dict(entry)

        if __DONT_USE_DATAFRAME is None:
            __DONT_USE_DATAFRAME = pd_entry
        else:
            __DONT_USE_DATAFRAME = pd.concat((__DONT_USE_DATAFRAME, pd_entry,), ignore_index=True)
            __DONT_USE_DATAFRAME.to_csv("data.csv")
            process(__DONT_USE_DATAFRAME)


    return response

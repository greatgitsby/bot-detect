import os
import sqlite3
from sqlalchemy import create_engine

from flask import request, session, Response, g
from hashlib import md5
from datetime import datetime
import uuid
import pandas as pd

DB_DRIVER = os.environ['DB_DRIVER'] if 'DB_DRIVER' in os.environ else 'sqlite3'
DB_URL = os.environ['DB_URL'] if 'DB_URL' in os.environ else 'log.db'


def __get_response_attrs(response: Response) -> dict:
    return {
        'resp_code': response.status_code,
        'resp_content_type': response.content_type,
        'resp_content_length': response.content_length,
    }


def __get_request_attrs() -> dict:
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

    if 'X-Forwarded-For' in header_keys:
        ip = request.headers.get('x-forwarded-for')

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


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        if DB_DRIVER == 'sqlite3':
            db = g._database = sqlite3.connect(DB_URL)
        elif DB_DRIVER == 'postgresql':
            db = g._database = create_engine(DB_URL).connect()
    return db

def init_request_log():
    db = get_db()
    sql = """
       -- auto-generated definition
        create table if not exists requests
        (
            "index"             INTEGER,
            ip                  TEXT,
            sess_id             TEXT,
            time                TIMESTAMP,
            req_method          TEXT,
            req_path            TEXT,
            req_depth           INTEGER,
            ua                  TEXT,
            referer             TEXT,
            header_hash         TEXT,
            resp_code           INTEGER,
            resp_content_type   TEXT,
            resp_content_length INTEGER
        );

        create index if not exists ix_requests_index
            on requests ("index");
    """
    db.execute(sql)


def add_new_entry(entry: pd.DataFrame):
    entry.to_sql('requests', get_db(), if_exists='append')


def get_request_log() -> pd.DataFrame:
    init_request_log()
    return pd.read_sql('SELECT * FROM requests', get_db())


def request_handler(*args, **kwargs):

    if g and '__request_attrs__' not in g:
        g.__request_attrs__ = __get_request_attrs()


def response_handler(response: Response):
    if g and '__request_attrs__' in g:
        entry = {}

        request_log_entry = dict(g.__request_attrs__)
        response_log_entry = dict(__get_response_attrs(response))

        entry.update(request_log_entry)
        entry.update(response_log_entry)

        for k in entry.keys():
            entry[k] = [entry[k]]

        pd_entry = pd.DataFrame.from_dict(entry)

        add_new_entry(pd_entry)

    return response

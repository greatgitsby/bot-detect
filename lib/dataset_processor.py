import pandas as pd
import numpy as np

# Disable copy warning - the warning is for
# a different use case than mine
# https://stackoverflow.com/a/20627316
pd.options.mode.chained_assignment = None  # default='warn'


def get_session_stats_for_ip(logs: pd.DataFrame, ip: str) -> pd.DataFrame:
    if 'ip' not in logs:
        return pd.DataFrame()

    logs_from_ip = logs[logs['ip'] == ip]

    return __get_session_stats_from_df(logs_from_ip)


def __get_session_stats_from_df(df: pd.DataFrame) -> pd.DataFrame:

    # Sort all requests by time
    df.sort_values(by='time', ascending=False)

    df['time'] = pd.to_datetime(df['time'])

    first_req, last_req = df.head(1), df.tail(1)

    page_requests = df['req_path'].value_counts()

    # Features
    num_requests = len(df)
    num_sessions = len(df['sess_id'].unique())
    num_unique_user_agents = len(df['ua'].unique())
    num_unique_header_hashes = len(df['header_hash'].unique())
    num_bytes_requested = df['resp_content_length'].sum()

    num_requests_GET = len(df[df['req_method'] == "GET"])
    num_requests_HEAD = len(df[df['req_method'] == "HEAD"])
    num_requests_POST = len(df[df['req_method'] == "POST"])

    num_request_codes_3XX = len(df['resp_code'].between(300, 399))
    num_request_codes_4XX = len(df['resp_code'].between(400, 499))

    if len(page_requests) > 0:
        max_requests_for_one_page = page_requests[page_requests.argmax()]
        avg_requests_per_page = np.average(page_requests)
        std_dev_page_depth = np.std(df['req_depth'])
    else:
        max_requests_for_one_page = 0
        avg_requests_per_page = 0
        std_dev_page_depth = 0

    # Max consec. requests for a page
    group_paths = (df['req_path'] != df['req_path'].shift()).cumsum()
    max_consecutive_requests_for_one_page = max(list([len(x) for _, x in df.groupby(group_paths)]))
    pct_consecutive_requests_for_one_page = max_consecutive_requests_for_one_page / len(df)

    first_req_time = first_req['time']
    last_req_time = last_req['time']

    first_req_ts = (first_req_time.iloc[0])
    last_req_ts = (last_req_time.iloc[0])

    sess_time_secs = (last_req_ts - first_req_ts).total_seconds()
    browse_speed_secs = (num_requests / sess_time_secs) if sess_time_secs != 0 else 0

    inter_req_times = (df["time"] - df["time"].shift(1)) / np.timedelta64(1, "s")
    avg_inter_req_time = np.average(inter_req_times.dropna())
    std_dev_inter_req_time = np.std(inter_req_times.dropna())

    num_unique_refers = len(df['referer'].dropna().unique())
    pct_referer = len(df['referer'].dropna()) / len(df['referer'])
    pct_no_referer = len(df[df['referer'].isnull()]) / len(df['referer'])

    """
    req_images = df[df['resp_content_type'].str.contains("image")]
    req_css = df[df['resp_content_type'].str.contains("css")]
    req_json = df[df['resp_content_type'].str.contains("json")]
    req_javascript = df[df['resp_content_type'].str.contains("javascript")]

    pct_images = len(req_images) / len(df)
    pct_css = len(req_css) / len(df)
    pct_json = len(req_json) / len(df)
    pct_javascript = len(req_javascript) / len(df)
    """

    session_log_dict = {
        'num_sessions': num_sessions,
        'num_unique_user_agents': num_unique_user_agents,
        'num_unique_header_hashes': num_unique_header_hashes,
        'num_requests': num_requests,
        'num_bytes_requested': num_bytes_requested,
        'num_requests_GET': num_requests_GET,
        'num_requests_HEAD': num_requests_HEAD,
        'num_requests_POST': num_requests_POST,
        'num_request_codes_3XX': num_request_codes_3XX,
        'num_request_codes_4XX': num_request_codes_4XX,
        'max_requests_for_one_page': max_requests_for_one_page,
        'avg_requests_per_pag': avg_requests_per_page,
        'std_dev_page_depth': std_dev_page_depth,
        'max_consecutive_requests_for_one_page': max_consecutive_requests_for_one_page,
        'pct_consecutive_requests_for_one_page': pct_consecutive_requests_for_one_page,
        'sess_time_secs': sess_time_secs,
        'browse_speed_secs': browse_speed_secs,
        'avg_inter_req_time': avg_inter_req_time,
        'std_dev_inter_req_time': std_dev_inter_req_time,
        'num_unique_refers': num_unique_refers,
        'pct_referer': pct_referer,
        'pct_no_referer': pct_no_referer,
    }

    for k in session_log_dict.keys():
        session_log_dict[k] = [session_log_dict[k]]

    return pd.DataFrame.from_dict(session_log_dict)


def process(logs: pd.DataFrame):
    session_log = None
    unique_ips = logs["ip"].unique()

    for ip in unique_ips:

        session_log_entry = get_session_stats_for_ip(logs, ip)

        if session_log is None:
            session_log = session_log_entry
        else:
            session_log = pd.concat((session_log, session_log_entry), ignore_index=True)

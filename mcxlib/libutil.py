import os
from datetime import datetime, timedelta, date
import requests
import numpy as np
from dateutil.relativedelta import relativedelta
import pandas as pd
from mcxlib.constants import *
from mcxlib.logger import mylogger

header = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/111.0.0.0 Safari/537.36",
    "Sec-Fetch-User": "?1", "Accept": "*/*", "Sec-Fetch-Site": "none", "Sec-Fetch-Mode": "navigate",
    "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
    }


class CalenderNotFound(Exception):
    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        super(CalenderNotFound, self).__init__(message)


class MCXdataNotFound(Exception):
    def __init__(self, message):
        super(MCXdataNotFound, self).__init__(message)


def validate_date_param(from_date:str, to_date:str, period:str):
    if not period and (not from_date or not to_date):
        raise ValueError(' Please provide the valid parameters')
    elif period and period.upper() not in equity_periods:
        raise ValueError(f'period = {period} is not a valid value')

    try:
        if not period:
            from_date = datetime.strptime(from_date, dd_mm_yyyy)
            to_date = datetime.strptime(to_date, dd_mm_yyyy)
            time_delta = (to_date - from_date).days
            if time_delta < 1:
                raise ValueError(f'to_date should greater than from_date ')
    except Exception as e:
        print(e)
        raise ValueError(f'either or both from_date = {from_date} || to_date = {to_date} are not valid value')


def derive_from_and_to_date(from_date:str = None, to_date:str = None, period:str = None):
    if not period:
        return from_date, to_date
    today = date.today()
    conditions = [period.upper()=='1D',
                  period.upper()=='1W',
                  period.upper()=='1M',
                  period.upper()=='6M',
                  period.upper()=='1Y'
                  ]
    value = [today - timedelta(days=1),
             today - timedelta(weeks=1),
             today - relativedelta(months=1),
             today - relativedelta(months=6),
             today - relativedelta(months=12)]

    f_date = np.select(conditions,value, default=(today - timedelta(days=1)))
    from_date = pd.to_datetime(str(f_date)).strftime(dd_mm_yyyy)
    today = today.strftime(dd_mm_yyyy)
    return from_date, today


def cleaning_column_name(col:list):
    unwanted_str_list = ['FH_', 'EOD_', 'HIT_']
    new_col=col
    for unwanted in unwanted_str_list:
        new_col = [name.replace(f'{unwanted}', '') for name in new_col]
    return new_col


def cleaning_mcs_symbol(symbol):
    symbol = symbol.replace('&','%26')  #URL Parse for Stocks Like M&M Finance
    return symbol.upper()


def mcx_urlfetch(url):
    r_session = requests.session()
    mcx_live = r_session.get("https://www.mcxindia.com/home", headers=header)
    return r_session.get(url, headers=header)


def get_mcxlib_path():
    """
    Extract isap file path
    """
    mydir = os.getcwd()
    return mydir.split(r'\mcxlib', 1)[0]



# if __name__ == '__main__':
#     # data = derive_from_and_to_date('6M')
#     print(trading_holiday_calendar())
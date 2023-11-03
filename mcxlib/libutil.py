from datetime import datetime
import os

header = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Content-Type': 'application/json',
        'Cookie': 'ASP.NET_SessionId=p4dkpr24k2j2ck1w2qnov1h5',
        'Origin': 'https://www.mcxindia.com',
        'Referer': 'https://www.mcxindia.com/market-data/market-watch',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="118", "Brave";v="118", "Not=A?Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
        }


class CalenderNotFound(Exception):
    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        super(CalenderNotFound, self).__init__(message)


class MCXdataNotFound(Exception):
    def __init__(self, message):
        super(MCXdataNotFound, self).__init__(message)


def get_headers(use_for:str = 'market-watch'):
    return {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Content-Type': 'application/json',
        'Origin': 'https://www.mcxindia.com',
        'Referer': f'https://www.mcxindia.com/market-data/{use_for}',
        'Sec-GPC': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="118", "Brave";v="118", "Not=A?Brand";v="99"',
        'sec-ch-ua-platform': '"Windows"'
    }


def validate_date_param(start_date:str, end_date:str):
    if not start_date or not end_date:
        raise ValueError(' Please provide the valid parameters')
    try:
        start_date = datetime.strptime(start_date, '%Y%m%d')
        end_date = datetime.strptime(end_date, '%Y%m%d')
        time_delta = (end_date - start_date).days
        if time_delta < 1:
            raise ValueError(f'end_date should greater than start_date ')
        elif time_delta > 365:
            raise ValueError(f'Date range cannot be greater than 365 days')
    except Exception as e:
        print(e)
        raise ValueError(f'either or both start_date = {start_date} || end_date = {end_date} are not valid value')


def get_mcxlib_path():
    """
    Extract isap file path
    """
    mydir = os.getcwd()
    return mydir.split(r'\mcxlib', 1)[0]



# if __name__ == '__main__':
#     # data = derive_from_and_to_date('6M')
#     print(trading_holiday_calendar())

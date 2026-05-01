import pandas as pd
from mcxlib.libutil import *
import json
import calendar
import re
from datetime import datetime, timedelta, timezone


MCX_TIMEZONE = timezone(timedelta(hours=5, minutes=30), "IST")
_MCX_DATE_PATTERN = re.compile(r"/Date\((-?\d+)(?:[+-]\d+)?\)/")


def _parse_mcx_datetime(value: str) -> datetime:
    match = _MCX_DATE_PATTERN.fullmatch(str(value).strip())
    if not match:
        raise ValueError(f"Invalid MCX datetime value: {value}")
    timestamp_ms = int(match.group(1))
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).astimezone(MCX_TIMEZONE)


def get_recent_expires(commodity:str = 'ALL') -> pd.DataFrame:
    """
    get recent expiry for commodity
    :param commodity: any of the list ['ALL', 'CRUDEOIL', 'COPPER', 'GOLD', 'GOLDM', 'NATURALGAS', 'SILVER', 'SILVERM', 'ZINC']
    :return: panda dataframe
    """
    url = "https://www.mcxindia.com/backpage.aspx/GetExpirywisePutCallRatio"
    payload = {}
    headers = get_headers(use_for='put-call-ratio')
    try:
        data_dict = post_json(url, headers=headers, payload=payload)
        data_df = pd.DataFrame.from_dict(data_dict['d']['Data'])
        data_df.drop(columns=['ExtensionData', 'Date', 'Ratio'], inplace=True)
    except Exception as e:
        raise ValueError(f" data not found / Invalid request  : MCX error:{e}")
    if not commodity == 'ALL':
        data_df = data_df[data_df['Symbol'] == commodity]
    if data_df.empty:
        raise ValueError("Apply a valid commodity name")
    return data_df


def get_market_watch() -> pd.DataFrame:
    """
    get live market watch on MCX
    :return: panda dataframe
    """
    url = "https://www.mcxindia.com/backpage.aspx/GetMarketWatch"
    payload = {}
    headers = get_headers(use_for='market-watch')
    try:
        data_dict = post_json(url, headers=headers, payload=payload)
        data_df = pd.DataFrame.from_dict(data_dict['d']['Data'])
        data_df.drop(columns=['__type', 'LTT'], inplace=True)
    except Exception as e:
        raise ValueError(f" No Data Found : MCX error:{e}")
    return data_df


def _filter_contract_rows(data_df: pd.DataFrame, filter_value: str, column_names) -> pd.DataFrame:
    value = str(filter_value).strip().upper()
    if value == 'ALL':
        return data_df
    if not value:
        raise ValueError("Apply a valid filter value")

    available_columns = [column for column in column_names if column in data_df.columns]
    if not available_columns:
        raise ValueError(f" No matching columns found to filter {filter_value}")

    exact_mask = pd.Series(False, index=data_df.index)
    contains_mask = pd.Series(False, index=data_df.index)
    for column in available_columns:
        column_data = data_df[column].fillna('').astype(str).str.strip().str.upper()
        exact_mask = exact_mask | (column_data == value)
        contains_mask = contains_mask | column_data.str.contains(value, regex=False)

    filtered_df = data_df[exact_mask].copy()
    if filtered_df.empty:
        filtered_df = data_df[contains_mask].copy()
    return filtered_df


def get_available_contracts(commodity:str = 'ALL',
                            instrument:str = 'ALL') -> pd.DataFrame:
    """
    get available contracts with live market details from MCX
    :param commodity: commodity name/symbol such as 'LEADMINI', 'CRUDEOIL', 'GOLD' or 'ALL'
    :param instrument: instrument type such as 'FUTCOM', 'FUTIDX', 'OPTCOM', 'OPTFUT' or 'ALL'
    :return: panda dataframe
    """
    url = "https://www.mcxindia.com/backpage.aspx/GetMarketWatch"
    payload = {}
    headers = get_headers(use_for='market-watch')
    try:
        data_dict = post_json(url, headers=headers, payload=payload)
        data_df = pd.DataFrame.from_dict(data_dict['d']['Data'])
        data_df.drop(columns=['__type'], inplace=True, errors='ignore')
    except Exception as e:
        raise ValueError(f" No contracts data found / Invalid request : MCX error:{e}")

    commodity_columns = [
        'Symbol',
        'Commodity',
        'CommodityName',
        'Product',
        'ProductName',
        'ContractName',
        'InstrumentIdentifier',
        'Instrument_Identifier',
    ]
    instrument_columns = [
        'InstrumentName',
        'Instrument',
        'InstrumentType',
        'Instrument_Type',
    ]

    data_df = _filter_contract_rows(data_df, commodity, commodity_columns)
    if data_df.empty:
        raise ValueError("Apply a valid commodity name")

    data_df = _filter_contract_rows(data_df, instrument, instrument_columns)
    if data_df.empty:
        raise ValueError("Apply a valid instrument name")

    data_df.reset_index(inplace=True)
    data_df.drop(columns='index', inplace=True)
    return data_df


def get_mcx_datetime() -> datetime:
    """
    get latest MCX market date and time
    :return: timezone-aware datetime object in IST
    """
    url = "https://www.mcxindia.com/backpage.aspx/GetMarketWatch"
    payload = {}
    headers = get_headers(use_for='market-watch')
    try:
        data_dict = post_json(url, headers=headers, payload=payload)
        timestamps = [
            _parse_mcx_datetime(item['LTT'])
            for item in data_dict['d']['Data']
            if item.get('LTT')
        ]
    except Exception as e:
        raise ValueError(f" No MCX date time found : MCX error:{e}")
    if not timestamps:
        raise ValueError(" No MCX date time found")
    return max(timestamps)


def get_heat_map() -> pd.DataFrame:
    """
    get live market heat map on MCX
    :return: panda dataframe
    """
    url = "https://www.mcxindia.com/backpage.aspx/GetHeatMap"
    payload = {}
    headers = get_headers(use_for='heatmap')
    try:
        data_dict = post_json(url, headers=headers, payload=payload)
        data_df = pd.DataFrame.from_dict(data_dict['d']['Data'])
        data_df.drop(columns=['__type', 'Dttm'], inplace=True)
    except Exception as e:
        raise ValueError(f" No heatmap Data Found : MCX error:{e}")
    return data_df


def get_top_gainers() -> pd.DataFrame:
    """
    get live market top gainers on MCX
    :return: panda dataframe
    """
    url = "https://www.mcxindia.com/backpage.aspx/GetGainer"
    payload = {}
    headers = get_headers(use_for='top-gainers')
    try:
        data_dict = post_json(url, headers=headers, payload=payload)
        data_df = pd.DataFrame.from_dict(data_dict['d']['Data'])
        data_df.drop(columns=['ExtensionData', 'LTT'], inplace=True)
    except Exception as e:
        raise ValueError(f" No top-gainers Data Found / Invalid request  : MCX error:{e}")
    return data_df


def get_top_losers() -> pd.DataFrame:
    """
    get live market top losers on MCX
    :return: panda dataframe
    """
    url = "https://www.mcxindia.com/backpage.aspx/GetLosers"
    payload = {}
    headers = get_headers(use_for='top-losers')
    try:
        data_dict = post_json(url, headers=headers, payload=payload)
        data_df = pd.DataFrame.from_dict(data_dict['d']['Data'])
        data_df.drop(columns=['ExtensionData', 'LTT'], inplace=True)
    except Exception as e:
        raise ValueError(f" No top-losers Data Found / Invalid request  : MCX error:{e}")
    return data_df


def get_most_active_contracts(instrument:str = 'ALL') -> pd.DataFrame:
    """
    get live market most active contract on MCX
    :param instrument: any value from the list ['ALL','FUTCOM','FUTIDX','OPTCOM','OPTFUT']
    :return: panda dataframe
    """
    headers = get_headers(use_for='most-active-contracts')
    url = "https://www.mcxindia.com/backpage.aspx/GetMostActiveContractByVolumeFilter"
    payload = json.dumps({
                            "InstrumentType": f'{instrument}'
                        })
    try:
        data_dict = post_json(url, headers=headers, payload=payload)
        data_df = pd.DataFrame.from_dict(data_dict['d']['Data'])
        data_df.drop(columns=['ExtensionData', 'Date', 'Unit'], inplace=True)
    except Exception as e:
        raise ValueError(f" No most-active-contracts Data Found / Invalid request : MCX error:{e}")
    return data_df


def get_most_active_puts_calls(option_type:str = 'PE',
                               product:str = 'ALL',
                               instrument:str = 'OPTFUT') -> pd.DataFrame:
    """
    get live market most active put/calls on MCX
    :param option_type: any value from the list ['PE','CE']
    :param product: any value from the list ['ALL','COPPER','CRUDEOIL','GOLD','GOLDM','NATURALGAS',
                                            'SILVER','SILVERM','ZINC']
    :param instrument: any value from the list ['OPTCOM','OPTIONS']
    :return: panda dataframe
    """
    headers = get_headers(use_for='most-active-puts-calls')
    url = "https://www.mcxindia.com/backpage.aspx/GetMostActiveOptionsContractsByVolume"
    payload_param = {'OptionType':f'{option_type}','Product':f'{product}','InstrumentType':f'{instrument}'}
    payload = f"{payload_param}"
    try:
        data_dict = post_json(url, headers=headers, payload=payload)
        data_df = pd.DataFrame.from_dict(data_dict['d']['Data'])
        data_df.drop(columns=['ExtensionData', 'LTT'], inplace=True)
    except Exception as e:
        raise ValueError(f" No Data Found / Invalid request : MCX error:{e}")
    return data_df


def get_bhav_copy(trade_date:str = '20230102',
                  instrument:str = 'ALL') -> pd.DataFrame:
    """
    get bhav copy
    :param trade_date: in str format : YYYYMMDD
    :param instrument: any value from the list ['ALL','FUTCOM','FUTIDX','OPTCOM','OPTFUT']
    :return: panda dataframe
    """
    headers = get_headers(use_for='bhavcopy')
    url = "https://www.mcxindia.com/backpage.aspx/GetDateWiseBhavCopy"
    payload_param = {'Date': f'{trade_date}', 'InstrumentName': f'{instrument}'}
    payload = f"{payload_param}"
    try:
        data_dict = post_json(url, headers=headers, payload=payload)
        data_df = pd.DataFrame.from_dict(data_dict['d']['Data'])
        data_df.drop(columns='__type', inplace=True)
    except Exception as e:
        raise ValueError(f" No Data Found / Invalid parameters : MCX error:{e}")
    return data_df


def get_historical_date_wise_data(start_date:str = '20230101',
                                  end_date:str = '20231103',) -> pd.DataFrame:
    """
    to get date wise history data in a panda dataframe
    Date range cannot be greater than 365 days
    :param start_date: in str format : YYYYMMDD
    :param end_date: in str format : YYYYMMDD
    :return: panda dataframe
    """
    headers = get_headers(use_for='historical-data')
    url = "https://www.mcxindia.com/backpage.aspx/GetHistoricalDataDetails"
    payload = json.dumps({
                            "GroupBy": "D",
                            "Segment": "ALL",
                            "CommodityHead": "ALL",
                            "Commodity": "ALL",
                            "Startdate": f"{start_date}",
                            "EndDate": f"{end_date}",
                            "InstrumentName": "ALL"
                        })
    validate_date_param(start_date=start_date, end_date=end_date)
    try:
        data_dict = post_json(url, headers=headers, payload=payload)
        data_df = pd.DataFrame.from_dict(data_dict['d']['Data'])
        data_df['Date'] = pd.to_datetime(data_df['Date'])
        data_df.drop(columns=['__type', 'Year', 'Month'], inplace=True)
    except Exception as e:
        raise ValueError(f" No Data Found / Invalid parameters : MCX error:{e}")
    return data_df


def get_mcx_icomdex_indices() -> pd.DataFrame:
    """
    get MCX iCOMDEX Indices
    :return: panda dataframe
    """
    url = "https://www.mcxindia.com/backpage.aspx/GetMCXIComdexIndicesDetails"
    payload = json.dumps({
        "Instrument_Identifier": "0",
        "Lang": "en"
    })
    headers = get_headers(use_for='mcx-icomdex-indices')
    try:
        data_dict = post_json(url, headers=headers, payload=payload)
        data_df = pd.DataFrame.from_dict(data_dict['d']['Data'])
        data_df.drop(columns=['__type'], inplace=True)
    except Exception as e:
        raise ValueError(f" No Data Found / Invalid request  : MCX error:{e}")
    return data_df


def get_pro_cli_details(trade_month:str = '202301') -> pd.DataFrame:
    """
    get PRO CLI Details for given month
    :param trade_month: in str format : YYYYMM
    :return: panda dataframe
    """
    headers = get_headers(use_for='pro-cli-details')
    url = "https://www.mcxindia.com/backpage.aspx/GetPROClientDetailsSegmentWise"
    payload = json.dumps({
        "GroupBy": "M",
        "Segment": "ALL",
        "CommodityHead": "ALL",
        "Commodity": "ALL",
        "Startdate": f"{trade_month}"
    })
    try:
        data_dict = post_json(url, headers=headers, payload=payload)
        data_df = pd.DataFrame.from_dict(data_dict['d']['Data'])
        data_df['Date'] = pd.to_datetime(data_df['Date'])
        data_df.drop(columns=['ExtensionData', 'TradingDate', 'Date'], inplace=True)
    except Exception as e:
        raise ValueError(f" No Data Found / Invalid parameters : MCX error:{e}")
    return data_df


def get_option_chain(commodity:str = 'CRUDEOIL', expiry:str = '15NOV2023') -> pd.DataFrame:
    """
    get live option chain from MCX site, the expiry date is different for different commodity
    :param commodity: any of the list ['CRUDEOIL', 'COPPER', 'GOLD', 'GOLDM', 'NATURALGAS', 'SILVER', 'SILVERM', 'ZINC']
    :param expiry: in the format od 'DDMMMYYYY' eg:'15NOV2023'
    :return: panda dataframe
    """
    headers = get_headers(use_for='option-chain')
    url = "https://www.mcxindia.com/backpage.aspx/GetOptionChain"
    payload_param = {'Commodity':f'{commodity}','Expiry':f'{expiry}'}
    payload = f"{payload_param}"
    try:
        data_dict = post_json(url, headers=headers, payload=payload)
        data_df = pd.DataFrame.from_dict(data_dict['d']['Data'])
        data_df.drop(columns=['ExtensionData', 'PE_LTT', 'CE_LTT', 'LTT', 'Symbol'], inplace=True)
        data_df = data_df[(data_df['CE_OpenInterest']>0) | (data_df['PE_OpenInterest']>0)].copy()
    except Exception as e:
        raise ValueError(f" Invalid parameters : MCX error:{e}")
    data_df.reset_index(inplace=True)
    data_df.drop(columns='index', inplace=True)
    return data_df


def get_put_call_ratio(ratio_type:str = 'expiry_wise') -> pd.DataFrame:
    """
    get recent expiry wise put call ratio
    :param ratio_type: 'expiry_wise' or 'commodity_wise'
    :return: panda dataframe
    """
    if ratio_type =='expiry_wise':
        url = "https://www.mcxindia.com/backpage.aspx/GetExpirywisePutCallRatio"
    elif ratio_type == 'commodity_wise':
        url = "https://www.mcxindia.com/backpage.aspx/GetCommoditywisePutCallRatio"
    else:
        raise ValueError(" Please apply valid ratio type")
    payload = {}
    headers = get_headers(use_for='put-call-ratio')
    try:
        data_dict = post_json(url, headers=headers, payload=payload)
        data_df = pd.DataFrame.from_dict(data_dict['d']['Data'])
        data_df.drop(columns=['ExtensionData', 'Date'], inplace=True)
    except Exception as e:
        raise ValueError(f" call put ratio data not found / Invalid request  : MCX error:{e}")
    return data_df


def get_category_wise_turnover(year:int = 2023, month_number:int = 9) -> pd.DataFrame:
    """
    get the category wise turnover data
    :param year: int format : YYYY
    :param month_number: int between (1 to 12)
    :return: pandas dataframe
    """
    month_long = calendar.month_name[month_number].lower()
    month_short = calendar.month_abbr[month_number].lower()
    try:
        url = f"https://www.mcxindia.com/docs/default-source/market-data/historicaldata/{str(year)}/{month_long}/" \
            f"category-wise-turnover-{month_short}-{str(year)}.xlsx"
        data_df = pd.read_excel(url, skiprows=2, skipfooter=9)
    except Exception as e:
        raise ValueError(f" apply valid parameter : MCX error:{e}")
    return data_df


def get_category_wise_oi(year:int = 2023, month_number:int = 9) -> pd.DataFrame:
    """
    get the category wise open interest data
    :param year: int format : YYYY
    :param month_number: int between (1 to 12)
    :return: pandas dataframe
    """
    month_long = calendar.month_name[month_number].lower()
    month_short = calendar.month_abbr[month_number].lower()
    try:
        url = f"https://www.mcxindia.com/docs/default-source/market-data/historicaldata/{str(year)}/{month_long}/" \
              f"category-wise-oi-{month_short}-{str(year)}.xlsx"
        data_df = pd.read_excel(url, skiprows=3, skipfooter=8)
    except Exception as e:
        raise ValueError(f" apply valid parameter : MCX error:{e}")
    data_df.columns = ['Date', 'Commodity', 'Instrument', 'Open Interest', 'FPOs/ Farmers(Long OI)',
                       'FPOs/ Farmers(Short OI)', 'VCPs/ Hedger(Long OI)', 'VCPs/ Hedger(Short OI)',
                       'Proprietary traders(Long OI)', 'Proprietary traders(Short OI)',
                       'Domestic Financial institutional investors(Long OI)',
                       'Domestic Financial institutional investors(Short OI)', 'Foreign Participants(Long OI)',
                       'Foreign Participants(Short OI)', 'Others(Long OI)', 'Others(Short OI)']
    return data_df


def get_ccl_delivery(year:int = 2023, month_number:int = 9) -> pd.DataFrame:
    """
    get the ccl delivery data
    :param year: int format : YYYY
    :param month_number: int between (1 to 12)
    :return: pandas dataframe
    """
    month_long = calendar.month_name[month_number].lower()
    # month_short = calendar.month_abbr[month_number].lower()
    try:
        url = f"https://www.mcxindia.com/docs/default-source/market-data/historicaldata/{str(year)}/{month_long}/" \
            f"ccl_delivery.xlsx"
        data_df = pd.read_excel(url)
    except Exception as e:
        raise ValueError(f" apply valid parameter : MCX error:{e}")
    data_df.dropna(inplace=True)
    data_df.reset_index(inplace=True)
    data_df.drop(columns='index', inplace=True)
    return data_df


def get_trading_statistics(year:int = 2023, month_number:int = 9) -> pd.DataFrame:
    """
    get the trading statistics data from MCX
    :param year: int format : YYYY
    :param month_number: int between (1 to 12)
    :return: pandas dataframe
    """
    month_long = calendar.month_name[month_number].lower()
    month_short = calendar.month_abbr[month_number].lower()
    try:
        url = f"https://www.mcxindia.com/docs/default-source/market-data/historicaldata/{str(year)}/{month_long}/" \
            f"trading-statistics-{month_short}-{str(year)}.xlsx"
        data_df = pd.read_excel(url, skipfooter=5)
    except Exception as e:
        raise ValueError(f" apply valid parameter : MCX error:{e}")
    data_df.rename(columns={"Mode of Trading (% of Turnover)": "Mode of ALGO Trading (% of Turnover)",
                            "Unnamed: 25": "Mode of Non-ALGO Trading (% of Turnover)"},inplace=True)
    data_df.dropna(inplace=True)
    data_df.reset_index(inplace=True)
    data_df.drop(columns='index', inplace=True)
    return data_df


if __name__ == '__main__':
    import mcxlib
    df = mcxlib.get_recent_expires(commodity='COPPER')
    print(df.columns)
    print(df)

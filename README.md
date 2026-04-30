# mcxlib

`mcxlib` is a Python library for fetching publicly available market data from the MCX India website and returning it as `pandas` DataFrames.

It provides a lightweight wrapper around common MCX endpoints so you can pull market snapshots, derivatives data, and historical reports directly into your Python workflows.

## What It Provides

- Live market data such as market watch, available contracts, heat map, top gainers, and top losers
- Derivatives data such as option chain, put-call ratio, and most active contracts
- Historical reports such as bhav copy, date-wise historical data, and trading statistics
- MCX index and participant-level datasets such as iCOMDEX indices and PRO/CLI details

## Installation

Install from PyPI:

```bash
pip install mcxlib
```

Upgrade an existing installation:

```bash
pip install --upgrade mcxlib
```

If you are working from source:

```bash
pip install -r requirements.txt
pip install -e .
```

## Dependencies

The project relies mainly on:

- `pandas`
- `requests`
- `xlrd`

Some MCX datasets are published as Excel files, so spreadsheet-reading support is required for part of the API.

## Quick Start

```python
import mcxlib

market_watch = mcxlib.get_market_watch()
print(market_watch.head())

bhav_copy = mcxlib.get_bhav_copy(
    trade_date="20231102",
    instrument="ALL",
)

option_chain = mcxlib.get_option_chain(
    commodity="CRUDEOIL",
    expiry="15NOV2023",
)

historical_data = mcxlib.get_historical_data(
    start_date="20230101",
    end_date="20231103",
)
```

## Public API

All exported functions return a `pandas.DataFrame`.

### Live Market Data

- `get_market_watch()`
- `get_available_contracts(commodity="ALL", instrument="ALL")`
- `get_heat_map()`
- `get_top_gainers()`
- `get_top_losers()`
- `get_most_active_contracts(instrument="ALL")`
- `get_most_active_puts_calls(option_type="PE", product="ALL", instrument="OPTFUT")`

### Options and Sentiment Data

- `get_recent_expires(commodity="ALL")`
- `get_option_chain(commodity="CRUDEOIL", expiry="15NOV2023")`
- `get_put_call_ratio(ratio_type="expiry_wise")`

### Historical and Report Data

- `get_bhav_copy(trade_date="YYYYMMDD", instrument="ALL")`
- `get_historical_date_wise_data(start_date="YYYYMMDD", end_date="YYYYMMDD")`
- `get_historical_data(start_date="YYYYMMDD", end_date="YYYYMMDD")`
- `get_category_wise_turnover(year=2023, month_number=9)`
- `get_category_wise_oi(year=2023, month_number=9)`
- `get_trading_statistics(year=2023, month_number=9)`
- `get_ccl_delivery(year=2023, month_number=9)`

### Index and Participant Data

- `get_mcx_icomdex_indices()`
- `get_pro_cli_details(trade_month="YYYYMM")`

## Parameter Notes

- Dates for `get_bhav_copy()` and `get_historical_data()` use `YYYYMMDD`
- `get_pro_cli_details()` uses month format `YYYYMM`
- `get_option_chain()` expiry uses `DDMMMYYYY`, for example `15NOV2023`
- Historical date-wise queries are limited by MCX to a maximum range of 365 days
- Valid parameter values depend on what MCX currently exposes for each endpoint

## Example Use Cases

Get the latest market watch data:

```python
import mcxlib

df = mcxlib.get_market_watch()
print(df.columns)
print(df.head())
```

Fetch live contracts for a commodity and convert them to JSON:

```python
import mcxlib

df = mcxlib.get_available_contracts(
    commodity="LEADMINI",
    instrument="FUTCOM",
)

print(df.to_json(orient="records"))
```

Fetch historical data for analysis:

```python
import mcxlib

df = mcxlib.get_historical_data(
    start_date="20230101",
    end_date="20230331",
)

print(df.head())
```

Fetch option chain data for a commodity:

```python
import mcxlib

df = mcxlib.get_option_chain(
    commodity="CRUDEOIL",
    expiry="15NOV2023",
)

print(df.head())
```

## Error Handling

Most functions raise `ValueError` when:

- Parameters are invalid
- MCX does not return data for the request
- The upstream MCX endpoint format changes

If you receive an error, first verify the parameter format and whether the requested dataset is currently available on the MCX website.

## Limitations

- This library depends on public MCX endpoints and report files remaining available
- Changes on the MCX website can break one or more functions without a package release
- Live data availability depends on MCX publishing current values at request time

## Contributing

Contributions are welcome. If you want to help:

- Open an issue: <https://github.com/RuchiTanmay/mcxlib/issues>
- Submit a pull request with a focused fix or enhancement
- Share examples or documentation improvements to help other users get started

## License

This project is licensed under the MIT License. See `LICENSE` for details.

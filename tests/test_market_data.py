from datetime import datetime, timezone
import unittest
from unittest.mock import patch

import mcxlib
import mcxlib.market_data as market_data


class MCXDatetimeTest(unittest.TestCase):
    def test_parse_mcx_datetime_returns_ist_datetime(self):
        parsed = market_data._parse_mcx_datetime("/Date(1777441209000)/")

        self.assertEqual(
            parsed,
            datetime(2026, 4, 29, 11, 10, 9, tzinfo=market_data.MCX_TIMEZONE),
        )

    def test_parse_mcx_datetime_accepts_offset_suffix(self):
        parsed = market_data._parse_mcx_datetime("/Date(0+0530)/")

        self.assertEqual(
            parsed,
            datetime.fromtimestamp(0, tz=timezone.utc).astimezone(
                market_data.MCX_TIMEZONE
            ),
        )

    def test_parse_mcx_datetime_accepts_default_negative_value(self):
        parsed = market_data._parse_mcx_datetime("/Date(-19800000)/")

        self.assertEqual(
            parsed,
            datetime.fromtimestamp(-19800, tz=timezone.utc).astimezone(
                market_data.MCX_TIMEZONE
            ),
        )

    def test_get_mcx_datetime_returns_latest_market_watch_ltt(self):
        response = {
            "d": {
                "Data": [
                    {"LTT": "/Date(1000)/"},
                    {"LTT": ""},
                    {},
                    {"LTT": "/Date(3000)/"},
                ]
            }
        }

        with patch.object(market_data, "post_json", return_value=response):
            result = market_data.get_mcx_datetime()

        self.assertEqual(
            result,
            datetime.fromtimestamp(3, tz=timezone.utc).astimezone(
                market_data.MCX_TIMEZONE
            ),
        )

    def test_get_mcx_datetime_is_exported(self):
        self.assertIs(mcxlib.get_mcx_datetime, market_data.get_mcx_datetime)


class AvailableContractsTest(unittest.TestCase):
    def setUp(self):
        self.response = {
            "d": {
                "Data": [
                    {
                        "__type": "MarketWatch",
                        "Symbol": "LEADMINI",
                        "InstrumentName": "FUTCOM",
                        "ContractName": "LEADMINI17DECFUT",
                        "LTP": 180.5,
                        "PercentChange": 1.25,
                        "ExpiryDate": "17DEC2026",
                    },
                    {
                        "__type": "MarketWatch",
                        "Symbol": "LEADMINI",
                        "InstrumentName": "OPTCOM",
                        "ContractName": "LEADMINI17DEC180CE",
                        "LTP": 3.2,
                        "PercentChange": -0.5,
                        "ExpiryDate": "17DEC2026",
                    },
                    {
                        "__type": "MarketWatch",
                        "Symbol": "GOLD",
                        "InstrumentName": "FUTCOM",
                        "ContractName": "GOLD05JUNFUT",
                        "LTP": 72800,
                        "PercentChange": 0.35,
                        "ExpiryDate": "05JUN2026",
                    },
                ]
            }
        }

    def test_get_available_contracts_filters_by_commodity_and_instrument(self):
        with patch.object(market_data, "post_json", return_value=self.response):
            result = market_data.get_available_contracts(
                commodity="LEADMINI",
                instrument="FUTCOM",
            )

        self.assertEqual(len(result), 1)
        self.assertEqual(result.loc[0, "ContractName"], "LEADMINI17DECFUT")
        self.assertEqual(result.loc[0, "LTP"], 180.5)
        self.assertNotIn("__type", result.columns)

    def test_get_available_contracts_can_filter_by_contract_name(self):
        with patch.object(market_data, "post_json", return_value=self.response):
            result = market_data.get_available_contracts(
                commodity="LEADMINI17DECFUT",
            )

        self.assertEqual(len(result), 1)
        self.assertEqual(result.loc[0, "Symbol"], "LEADMINI")

    def test_get_available_contracts_rejects_unknown_commodity(self):
        with patch.object(market_data, "post_json", return_value=self.response):
            with self.assertRaises(ValueError):
                market_data.get_available_contracts(commodity="UNKNOWN")

    def test_get_available_contracts_is_exported(self):
        self.assertIs(mcxlib.get_available_contracts, market_data.get_available_contracts)


if __name__ == "__main__":
    unittest.main()

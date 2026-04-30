import unittest
from unittest.mock import patch

import mcxlib
import mcxlib.market_data as market_data


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

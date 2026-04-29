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


if __name__ == "__main__":
    unittest.main()

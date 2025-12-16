import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import datetime
import time as base_time

# Add parent directory to path to import iceberg
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iceberg_utils import get_current_time_info, format_currency, convert_dollars_to_cents, id_generator
import string


class TestIcebergUtils(unittest.TestCase):
    @patch('iceberg_utils.datetime')
    @patch('iceberg_utils.time')
    def test_get_current_time_info(self, mock_time, mock_datetime):
        # Setup mock for datetime.now()
        # We use a real datetime object so methods like weekday(), month, etc work naturally
        fixed_date = datetime.datetime(2023, 10, 27, 14, 30, 0)
        
        # mock_datetime is the module 'datetime' imported in iceberg.py
        # We want mock_datetime.datetime.now() to return fixed_date
        mock_datetime.datetime.now.return_value = fixed_date
        
        # Also need to ensure other attributes like timedelta are present if used (though get_current_time_info doesn't use it, others might)
        # But get_current_time_info only uses datetime.datetime.now()
        
        # Setup time.tzname
        mock_time.daylight = 0
        mock_time.tzname = ('EST', 'EDT')
        
        expected_time_str = "Friday, 10/27/2023  -  14:30 EST"
        expected_timestamp_str = "Friday, 10/27/2023  -  14:30:00 EST"
        
        result_time, result_timestamp = get_current_time_info()
        
        self.assertEqual(result_time, expected_time_str)
        self.assertEqual(result_timestamp, expected_timestamp_str)

    def test_format_currency(self):
        # Test zero
        self.assertEqual(format_currency(0), "$0.00")
        self.assertEqual(format_currency("0"), "$0.00")
        
        # Test positive integers
        self.assertEqual(format_currency(12345), "$123.45")
        self.assertEqual(format_currency(5), "$0.05")
        self.assertEqual(format_currency(50), "$0.50")
        self.assertEqual(format_currency(100), "$1.00")
        self.assertEqual(format_currency(100000), "$1,000.00")
        
        # Test negative integers
        self.assertEqual(format_currency(-12345), "($123.45)")
        self.assertEqual(format_currency(-5), "($0.05)")
        self.assertEqual(format_currency(-50), "($0.50)")
        self.assertEqual(format_currency(-100), "($1.00)")
        self.assertEqual(format_currency(-100000), "($1,000.00)")

        # Test custom symbol
        self.assertEqual(format_currency(100, symbol='€'), "€1.00")

    def test_convert_dollars_to_cents(self):
        # Test valid inputs
        self.assertEqual(convert_dollars_to_cents("1.00"), 100)
        self.assertEqual(convert_dollars_to_cents("0.05"), 5)
        self.assertEqual(convert_dollars_to_cents("123.45"), 12345)
        self.assertEqual(convert_dollars_to_cents(10.50), 1050)
        
        # Test zero
        self.assertEqual(convert_dollars_to_cents("0"), 0)
        self.assertEqual(convert_dollars_to_cents(0), 0)
        
        # Test invalid inputs (should return None based on current implementation returning None implicitly via pass)
        self.assertIsNone(convert_dollars_to_cents("invalid"))

    def test_id_generator(self):
        # Test default length (30)
        id1 = id_generator()
        self.assertEqual(len(id1), 30)
        
        # Test custom length
        id2 = id_generator(size=10)
        self.assertEqual(len(id2), 10)
        
        # Test default characters (uppercase + digits)
        allowed_chars = string.ascii_uppercase + string.digits
        for char in id1:
            self.assertIn(char, allowed_chars)
            
        # Test custom characters
        custom_chars = "ABC"
        id3 = id_generator(size=5, chars=custom_chars)
        self.assertEqual(len(id3), 5)
        for char in id3:
            self.assertIn(char, custom_chars)


if __name__ == '__main__':
    unittest.main()

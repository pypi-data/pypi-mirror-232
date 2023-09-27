import unittest
from datetime import datetime, timedelta, timezone
import arrow as ar
import sys
sys.path.insert(0, '../src/simple_notifs')
from simple_notifs import utc_to_human

class TestTimeSince(unittest.TestCase):

    def test_seconds_1(self):
        """Test time delta in seconds"""
      
        dt = ar.utcnow()
        dt = dt.shift(seconds = -25)
        self.assertEqual(utc_to_human(dt), "25s")

    def test_seconds_2(self):
        dt = ar.utcnow()
        dt = dt.shift(seconds = -60)
        self.assertEqual(utc_to_human(dt), "1mi")

    def test_minutes_1(self):
        """Test time delta in minutes"""
        dt = ar.utcnow()
        dt = dt.shift(seconds = -61)
        self.assertEqual(utc_to_human(dt), "1mi")

    def test_minutes_2(self):
        dt = ar.utcnow()
        dt = dt.shift(seconds = -3600)
        self.assertEqual(utc_to_human(dt), "1h")

    def test_hours_1(self):
        """Test time delta in hours"""
        dt = ar.utcnow()
        dt = dt.shift(hours = -5)
        self.assertEqual(utc_to_human(dt), "5h")

    def test_hours_2(self):
        dt = ar.utcnow()
        dt = dt.shift(hours = -24)
        self.assertEqual(utc_to_human(dt), "1d")

    def test_days_1(self):
        """Test time delta in days"""
        dt = ar.utcnow()
        dt = dt.shift(days = -1)
        self.assertEqual(utc_to_human(dt), "1d")

    def test_days_2(self):
        dt = ar.utcnow()
        dt = dt.shift(days = -7)
        self.assertEqual(utc_to_human(dt), "1w")

    def test_weeks_1(self):
        """Test time delta in weeks"""
        dt = ar.utcnow()
        dt = dt.shift(days = -8)
        self.assertEqual(utc_to_human(dt), "1w")

    def test_weeks_2(self):
        dt = ar.utcnow()
        dt = dt.shift(days = -29)
        self.assertEqual(utc_to_human(dt), "4w")

    def test_months_1(self):
        """Test time delta in months"""
        dt = ar.utcnow()
        dt = dt.shift(days = -30)
        self.assertEqual(utc_to_human(dt), "1m")

    def test_months_2(self):
        dt = ar.utcnow()
        dt = dt.shift(days = -365)
        self.assertEqual(utc_to_human(dt), "1y")
        

    def test_years(self):
        """Test time delta in years"""
        dt = ar.utcnow()
        dt = dt.shift(days = -1200)
        self.assertEqual(utc_to_human(dt), "3y")

if __name__ == '__main__':
    unittest.main()
    





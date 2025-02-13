from unittest import TestCase

import unittest
from src.service.Trading import get_volume_data
import pandas as pd


class Test(TestCase):
    def test_get_volume_data(self):
        def test_get_volume_data_returns_dataframe(self):
            df = get_volume_data()
            self.assertIsInstance(df, pd.DataFrame)

        def test_get_volume_data_columns(self):
            df = get_volume_data()
            expected_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'MA5']
            self.assertEqual(df.columns.tolist(), expected_columns)

        def test_get_volume_data_ma5_calculation(self):
            df = get_volume_data()
            ma5 = df['volume'].rolling(window=5).mean()
            self.assertTrue(df['MA5'].equals(ma5))

    if __name__ == '__main__':
        unittest.main()

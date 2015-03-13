__author__ = 'max'

import unittest
from mock import Mock, patch
from test_utils import assert_calls_amount
from lib import fix_market_url


class InitTestCase(unittest.TestCase):
    def test_fix_market_url(self):
        lstrip = Mock(return_value='test')
        with patch('string.lstrip', lstrip):
            fix_market_url('')

        lstrip.assert_called_once_with("market://")
        assert_calls_amount(lstrip, 1)



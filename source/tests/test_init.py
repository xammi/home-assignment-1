__author__ = 'max'

import unittest
from mock import Mock, patch
from test_utils import assert_calls_amount
from lib import fix_market_url


class InitTestCase(unittest.TestCase):
    def test_fix_market_url(self):
        lstrip = Mock(return_value='test')

        result = fix_market_url('market://_my_app')
        assert result == "http://play.google.com/store/apps/_my_app"

        result = fix_market_url('market://my_app')
        assert result == "http://play.google.com/store/apps/y_app"

        result = fix_market_url('market://market')
        assert result == "http://play.google.com/store/apps/"

        # lstrip should be replaced with re.sub(url, re.compile('^market://'))



__author__ = 'max'

import unittest
from mock import Mock, MagicMock, patch
from test_utils import assert_calls_amount
from lib import *
import re

class InitTestCase(unittest.TestCase):
    def test_to_unicode(self):
        result = to_unicode('test')
        assert result == 'test'

    def test_to_str(self):
        result = to_str('test')
        assert result == 'test'

    def test_get_counters(self):
        match = Mock(return_value=True)
        with patch('re.match', match):
            result = get_counters('test')

        counters = []
        for counter_name, regexp in COUNTER_TYPES:
            counters.append(counter_name)

        assert_calls_amount(match, len(COUNTER_TYPES))
        assert result == counters

    def test_check_for_meta(self):
        html = '<meta http-equiv="refresh" content="5; url=test">'
        m = re.match(r"(\w+)", "test")
        search = Mock(return_value=m)
        with patch('re.search', search):
            result = check_for_meta(html, 'http://test.com/')

        assert result == "http://test.com/test"
        assert_calls_amount(search, 1)

    def test_check_for_meta_none(self):
        html = '<meta http-equiv="refresh" content="5 url=test">'
        result = check_for_meta(html, 'http://test.com/')
        assert result == None

    def test_fix_market_url(self):
        result = fix_market_url('market://_my_app')
        assert result == "http://play.google.com/store/apps/_my_app"

    def test_make_pycurl_request(self):
        curl = MagicMock()
        curl.perform = Mock()
        curl.getinfo.return_value = 'url'

        string_io = MagicMock()
        string_io.getvalue.retun_value = 'content'

        with patch('pycurl.Curl', Mock(return_value=curl)):
            with patch('lib.StringIO', Mock(return_value=string_io)):
                content, redirect_url = make_pycurl_request('test', 1000, 'user')

        assert_calls_amount(curl, 8)
        assert redirect_url == 'url'

    def test_get_url(self):
        make_pycurl_request = Mock(return_value="123")
        with patch("lib.make_pycurl_request", make_pycurl_request):
            pass







import unittest
from mock import Mock, MagicMock, patch
from lib import *

TEST_STRING = 'test'
MARKET_URL = 'http://play.google.com/store/apps/'
TEST_TIMEOUT = 5

class InitTestCase(unittest.TestCase):

    def test_to_unicode(self):
        result = to_unicode(TEST_STRING)
        assert result == TEST_STRING

    def test_to_str(self):
        result = to_str(TEST_STRING)
        assert result == TEST_STRING

    def test_get_counters(self):
        match = Mock(return_value=True)
        with patch('re.match', match):
            result = get_counters('')

        counters = []
        for counter_name, regexp in COUNTER_TYPES:
            counters.append(counter_name)

        assert result == counters

    def test_check_for_meta(self):
        html = '<meta http-equiv="refresh" content="5; url=test">'
        result = check_for_meta(html, 'http://test.com/')
        assert result == "http://test.com/test"


    def test_check_for_meta_none(self):
        html = '<meta http-equiv="refresh" content="5 url=test">'
        result = check_for_meta(html, 'http://test.com/')
        assert result == None

    def test_fix_market_url(self):
        result = fix_market_url('market://_my_app')
        assert result == MARKET_URL + '_my_app'

    def test_make_pycurl_request(self):
        curl = MagicMock()
        curl.perform = Mock()
        curl.getinfo.return_value = TEST_STRING

        with patch('pycurl.Curl', Mock(return_value=curl)):
            content, redirect_url = make_pycurl_request('', 1000, 'mozilla')

        assert redirect_url == TEST_STRING

    def test_get_url(self):
        make_pycurl_request = Mock(return_value=(TEST_STRING, TEST_STRING))
        with patch("lib.make_pycurl_request", make_pycurl_request):
            result = get_url('', TEST_TIMEOUT)

        assert result == (TEST_STRING, 'http_status', TEST_STRING)

    def test_get_url_ok_redirect(self):
        url = 'http://odnoklassniki.ru/st.redirect'
        make_pycurl_request = Mock(return_value=(TEST_STRING, url))
        with patch("lib.make_pycurl_request", make_pycurl_request):
            result = get_url('', TEST_TIMEOUT)

        assert result == (None, None, TEST_STRING)

    def test_get_url_except_value(self):
        make_pycurl_request = Mock(side_effect=ValueError)
        with patch("lib.make_pycurl_request", make_pycurl_request):
            result = get_url(TEST_STRING, TEST_TIMEOUT)

        assert result == (TEST_STRING, 'ERROR', None)

    def test_get_url_redirect_meta(self):
        make_pycurl_request = Mock(return_value=(TEST_STRING, None))
        check_for_meta = Mock(return_value='market://')
        with patch("lib.make_pycurl_request", make_pycurl_request):
            with patch("lib.check_for_meta", check_for_meta):
                result = get_url('', TEST_TIMEOUT)

        assert result == (MARKET_URL, 'meta_tag', TEST_STRING)






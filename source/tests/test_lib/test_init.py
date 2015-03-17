import unittest
from mock import Mock, patch
from lib import *

TEST_STRING = 'test'
TEST_URL = 'url'
TEST_REDIRECT_URL = 'redirect'
TEST_CONTENT = 'content'
MARKET_URL = 'http://play.google.com/store/apps/'
TEST_TIMEOUT = 5

class InitTestCase(unittest.TestCase):

    def test_to_unicode(self):
        assert to_unicode(TEST_STRING.decode('utf-8')) == 'test'

    def test_to_str(self):
        assert to_str(TEST_STRING.encode('utf-8')) == TEST_STRING

    def test_get_counters(self):
        match = Mock(return_value=True)
        with patch('re.match', match):
            result = get_counters('')

        counters = []
        for counter_name, regexp in COUNTER_TYPES:
            counters.append(counter_name)

        assert result == counters

    def test_get_counters_false(self):
        match = Mock(return_value=False)
        with patch('re.match', match):
            result = get_counters('')

        counters = []
        assert result == counters

    def test_check_for_meta(self):
        html = '<meta http-equiv="refresh" content="5; url=test">'
        result = check_for_meta(html, 'http://test.com/')
        assert result == "http://test.com/test"


    def test_check_for_meta_none(self):
        html = '<meta http-equiv="refresh" content="5 url=test">'
        result = check_for_meta(html, 'http://test.com/')
        assert result is None

    def test_check_for_meta_none_meta(self):
        html = '<>'
        result = check_for_meta(html, 'http://test.com/')
        assert result is None

    def test_check_for_meta_content_none(self):
        html = '<meta http-equiv="refresh" content=";">'
        result = check_for_meta(html, 'http://test.com/')
        assert result is None

    def test_fix_market_url(self):
        result = fix_market_url('market://_my_app')
        assert result == MARKET_URL + '_my_app'

    def test_make_pycurl_request(self):
        curl = Mock()
        curl.perform = Mock()
        curl.getinfo.return_value = TEST_STRING

        with patch('pycurl.Curl', Mock(return_value=curl)):
            content, redirect_url = make_pycurl_request('', 1000, 'mozilla')

        assert redirect_url == TEST_STRING

    def test_make_pycurl_request_useragent_none(self):
        curl = Mock()
        curl.perform = Mock()
        curl.getinfo.return_value = TEST_STRING

        with patch('pycurl.Curl', Mock(return_value=curl)):
            content, redirect_url = make_pycurl_request('', 1000)

        assert redirect_url == TEST_STRING

    def test_make_pycurl_request_cur_getinfo_none(self):
        curl = Mock()
        curl.perform = Mock()
        curl.getinfo.return_value = None

        with patch('pycurl.Curl', Mock(return_value=curl)):
            content, redirect_url = make_pycurl_request('', 1000, 'mozilla')

        assert redirect_url is None

    def test_get_url(self):
        make_pycurl_request = Mock(return_value=(TEST_CONTENT, TEST_REDIRECT_URL))
        with patch("lib.make_pycurl_request", make_pycurl_request):
            result = get_url('', TEST_TIMEOUT)

        assert result == (TEST_REDIRECT_URL, REDIRECT_HTTP, TEST_CONTENT)

    def test_get_url_ignoring_ok_login_redirect(self):
        redirect_url = 'http://odnoklassniki.ru/st.redirect'
        make_pycurl_request = Mock(return_value=(TEST_CONTENT, redirect_url))
        with patch("lib.make_pycurl_request", make_pycurl_request):
            result = get_url('', TEST_TIMEOUT)

        assert result == (None, None, TEST_CONTENT)

    def test_get_url_except_value(self):
        make_pycurl_request = Mock(side_effect=ValueError)
        with patch("lib.make_pycurl_request", make_pycurl_request):
            result = get_url(TEST_CONTENT, TEST_TIMEOUT)

        assert result == (TEST_CONTENT, 'ERROR', None)

    def test_get_url_redirect_meta(self):
        make_pycurl_request = Mock(return_value=(TEST_CONTENT, None))
        check_for_meta = Mock(return_value='market://')
        with patch("lib.make_pycurl_request", make_pycurl_request):
            with patch("lib.check_for_meta", check_for_meta):
                result = get_url('', TEST_TIMEOUT)

        assert result == (MARKET_URL, REDIRECT_META, TEST_CONTENT)

    def test_get_url_new_redirect_url_none(self):
        make_pycurl_request = Mock(return_value=(TEST_CONTENT, None))
        check_for_meta = Mock(return_value=None)
        with patch("lib.make_pycurl_request", make_pycurl_request):
            with patch("lib.check_for_meta", check_for_meta):
                result = get_url('', TEST_TIMEOUT)

        assert result == (None, None, TEST_CONTENT)

    def test_get_redirect_history(self):
        url = 'http://odnoklassniki.ru/'
        result = get_redirect_history(url, TEST_TIMEOUT)
        assert result == ([], [url], [])

    def test_get_redirect_history_not_redirect(self):
        url = TEST_STRING
        get_url = Mock(return_value=(None, None, None))
        with patch("lib.get_url", get_url):
            result = get_redirect_history(url, TEST_TIMEOUT)

        assert result == ([], [url], [])

    def test_get_redirect_history_redirect_type_error(self):
        url = TEST_STRING
        get_url = Mock(return_value=(url, 'ERROR', None))
        with patch("lib.get_url", get_url):
            result = get_redirect_history(url, TEST_TIMEOUT)

        assert result == (['ERROR'], [url, url], [])

    def test_get_redirect_history_max_redirects(self):
        get_url = Mock(return_value=(TEST_URL, TEST_REDIRECT_URL, None))
        with patch("lib.get_url", get_url):
            result = get_redirect_history(TEST_URL, TEST_TIMEOUT, 1)

        assert result == ([TEST_REDIRECT_URL], [TEST_URL, TEST_URL], [])

    def test_get_redirect_history_counters(self):
        content = 'test mc.yandex.ru/metrika/watch.js test'
        get_url = Mock(return_value=(TEST_URL, TEST_REDIRECT_URL, content))
        with patch("lib.get_url", get_url):
            result = get_redirect_history(TEST_URL, TEST_TIMEOUT, 1)
        assert result == ([TEST_REDIRECT_URL], [TEST_URL, TEST_URL], ['YA_METRICA'])

    def test_prepare_url(self):
        url = 'http://sdf.example.com/dir 2/?name=123'
        assert prepare_url(url) == 'http://sdf.example.com/dir%202/?name=123'

    def test_prepare_url_none(self):
        assert prepare_url(None) == None

    def test_prepare_url_uncide_error(self):
        urlparse = Mock(return_value=('', u'.', '', '', '', ''))
        with patch("lib.urlparse", urlparse):
                result = prepare_url('')

        assert result == '//.'









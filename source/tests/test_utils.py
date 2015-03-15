__author__ = 'max'

import unittest
from mock import Mock, patch
from lib.utils import daemonize, create_pidfile


def assert_calls_amount(mock_obj, cnt):
    mock_calls = mock_obj.mock_calls
    assert len(mock_calls) == cnt


class UtilsTestCase(unittest.TestCase):
    def test_daemonize_zero(self):
        fork = Mock(return_value=0)
        setsid = Mock()
        _exit = Mock()

        with patch('os.fork', fork):
            with patch('os._exit', _exit):
                with patch('os.setsid', setsid):
                    daemonize()

        assert_calls_amount(fork, 2)
        assert_calls_amount(setsid, 1)
        assert_calls_amount(_exit, 0)

    def test_daemonize_exit(self):
        fork = Mock(return_value=1)
        setsid = Mock()
        _exit = Mock()

        with patch('os.fork', fork):
            with patch('os._exit', _exit):
                with patch('os.setsid', setsid):
                    daemonize()

        assert_calls_amount(fork, 1)
        _exit.assert_called_once_with(0)

    def test_create_pidfile(self):
        create_pidfile("test_pidfile")

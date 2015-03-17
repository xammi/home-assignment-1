__author__ = 'max'

import unittest
from mock import Mock, patch, mock_open, call
from lib.utils import daemonize, create_pidfile, load_config_from_pyfile, parse_cmd_args, \
    get_tube, spawn_workers, check_network_status
from tarantool_queue import tarantool_queue
from multiprocessing import Process


def assert_calls_amount(mock_obj, cnt):
    mock_calls = mock_obj.mock_calls
    assert len(mock_calls) == cnt


class UtilsTestCase(unittest.TestCase):
    def test_daemonize_zero(self):
        fork = Mock(return_value=0)

        with patch('os.fork', fork):
            with patch('os._exit') as _exit:
                with patch('os.setsid') as setsid:
                    daemonize()

        assert_calls_amount(fork, 2)
        setsid.assert_called_once_with()
        assert_calls_amount(_exit, 0)

    def test_daemonize_exit(self):
        fork = Mock(return_value=1)

        with patch('os.fork', fork):
            with patch('os._exit') as _exit:
                with patch('os.setsid'):
                    daemonize()

        fork.assert_called_with()
        _exit.assert_called_once_with(0)


    def test_daemonize_oserror(self):

        fork = Mock(side_effect=OSError)

        with patch('os.fork', fork):
            with self.assertRaises(Exception):
                daemonize()

    def test_daemonize_oserror2(self):
        fork = Mock(side_effect=[0, OSError])

        with patch('os.fork', fork):
            with patch('os.setsid') as setsid:
                with self.assertRaises(Exception):
                    daemonize()


    def test_daemonize_greater_zero(self):
        fork = Mock(side_effect=[0, 1])

        with patch('os.fork', fork):
            with patch('os._exit') as _exit:
                with patch('os.setsid') as setsid:
                    daemonize()

        assert_calls_amount(fork, 2)
        setsid.assert_called_once_with()
        assert_calls_amount(_exit, 1)

    def test_create_pidfile(self):
        pid = 42
        opener = mock_open()

        with patch('lib.utils.open', opener, create=True):
            with patch('os.getpid', Mock(return_value=pid)):
                create_pidfile('/file/path')

        opener.assert_called_once_with('/file/path', 'w')
        opener().write.assert_called_once_with(str(pid))

    def test_load_config_from_pyfile(self):
        filepath = '/test'

        def execfile(filepath, variables):
            variables['UPPER_CASE'] = 42
            variables['lower_case'] = 1

        with patch('__builtin__.execfile', side_effect=execfile):
            cfg = load_config_from_pyfile(filepath)

        self.assertEqual(cfg.UPPER_CASE, 42)
        self.assertFalse(hasattr(cfg, 'lower_case'))

    def test_parse_cmd_args_pid(self):
        cfg = '/test'
        pid = '/pid'
        args = parse_cmd_args(['-c', cfg, '-P', pid], 'test')

        self.assertEqual(args.config, cfg)
        self.assertEqual(args.pidfile, pid)
        self.assertFalse(args.daemon)

    def test_parse_cmd_pidfile(self):
        cfg = '/conf'
        pidfile = '/pidfile'
        parsed_args = parse_cmd_args(['-c', cfg, '-P', pidfile, '-d'])

        self.assertTrue(parsed_args.daemon)
        self.assertEqual(parsed_args.config, cfg)
        self.assertEqual(parsed_args.pidfile, pidfile)

    def test_get_tube(self):
        name = 'name'
        port = space = 42

        with patch.object(tarantool_queue.Queue, 'tube') as mock_queue:
            get_tube('host', port, space, name)

        mock_queue.assert_called_once_with(name)

    def test_spawn_workers(self):
        num = 42
        parent_pid = 1
        args = []

        with patch.object(Process, 'start') as mock_process:
            spawn_workers(num, 'target', args, parent_pid)

        calls = [call() for _ in range(0, num)]
        mock_process.assert_has_calls(calls)

    def test_check_network_status_error(self):
        check_url = 'http://ya.ru'
        timeout = 42
        mock_urlopen = Mock(side_effect=ValueError)

        with patch('urllib2.urlopen', mock_urlopen):
            result = check_network_status(check_url, timeout)

        self.assertFalse(result)

    def test_check_network_status(self):
        check_url = 'http://ya.ru'
        timeout = 42

        with patch('urllib2.urlopen') as mock_urlopen:
            result = check_network_status(check_url, timeout)

        mock_urlopen.assertTrue(result)

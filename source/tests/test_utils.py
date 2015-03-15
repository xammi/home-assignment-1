__author__ = 'max'

import unittest
from mock import Mock, patch, mock_open
from lib.utils import daemonize, create_pidfile, load_config_from_pyfile, parse_cmd_args


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
        pid = 42
        opener = mock_open()

        with patch('lib.utils.open', opener, create=True):
            with patch('os.getpid', Mock(return_value=pid)):
                create_pidfile('/file/path')

        opener.assert_called_once_with('/file/path', 'w')
        opener().write.assert_called_once_with(str(pid))

    def test_load_config_from_pyfile(self):
        filepath = '/test'

        def execfile_wrapper(filepath, variables):
            local_variables = {'A': 23}

        execfile = Mock(wraps=execfile_wrapper)
        with patch('__builtin__.execfile', execfile):
            cfg = load_config_from_pyfile(filepath)

        execfile.assert_called_once_with('/test', {})
        # self.assertEqual(cfg.A, 23)

    def test_parse_cmd_args_pid(self):
        cfg = '/test'
        pid = '/pid'
        args = parse_cmd_args(['-c', cfg, '-P', pid], 'test')
        self.assertTrue(args.config == cfg)
        self.assertTrue(args.pidfile == pid)
        self.assertFalse(args.daemon)

    def test_parse_cmd_pidfile(self):
        cfg = '/conf'
        pidfile = '/pidfile'
        parsed_args = parse_cmd_args(['-c', cfg, '-P', pidfile, '-d'])
        self.assertEqual(parsed_args.daemon, True)
        self.assertEqual(parsed_args.config, cfg)
        self.assertEqual(parsed_args.pidfile, pidfile)
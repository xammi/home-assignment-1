import unittest
from mock import Mock, patch
from redirect_checker import main, main_loop


EXIT_CODE = 1222


class RedirectCheckerTestCase(unittest.TestCase):

    def test_main_loop_network_ok(self):
        config = Mock(WORKER_POOL_SIZE=2, SLEEP=0)
        sleep = Mock(side_effect=KeyboardInterrupt)

        with patch('redirect_checker.sleep', sleep):
            with self.assertRaises(KeyboardInterrupt):
                with patch('redirect_checker.spawn_workers') as spawner:
                    with patch('redirect_checker.check_network_status', Mock(return_value=True)):
                        main_loop(config)

        spawner_calls = spawner.mock_calls
        self.assertEqual(len(spawner_calls), 1)

    def test_main_loop_network_ok_without_spawn(self):
        config = Mock(WORKER_POOL_SIZE=0, SLEEP=0)
        sleep = Mock(side_effect=KeyboardInterrupt)

        with patch('redirect_checker.sleep', sleep):
            with self.assertRaises(KeyboardInterrupt):
                with patch('redirect_checker.spawn_workers') as spawner:
                    with patch('redirect_checker.check_network_status', Mock(return_value=True)):
                        main_loop(config)

        spawner_calls = spawner.mock_calls
        self.assertEqual(len(spawner_calls), 0)

    def test_main_loop_network_down(self):
        config = Mock(WORKER_POOL_SIZE=0, SLEEP=0)
        sleep = Mock(side_effect=KeyboardInterrupt)
        children = [Mock(), Mock(), Mock()]

        with patch('redirect_checker.sleep', sleep):
            with self.assertRaises(KeyboardInterrupt):
                with patch('redirect_checker.active_children', Mock(return_value=children)):
                    with patch('redirect_checker.check_network_status', Mock(return_value=False)):
                        main_loop(config)

        for child in children:
            child.terminate.assert_called_once_with()

    def test_main_daemonize(self):
        args = ['1', '-c', '/conf', '-d']
        conf = Mock(LOOGING={}, EXIT_CODE=EXIT_CODE)

        with patch("redirect_checker.daemonize") as mock_daemonize:
            with patch("redirect_checker.load_config_from_pyfile", Mock(return_value=conf)):
                with patch("redirect_checker.main_loop") as mock_main_loop:
                    with patch("os.path.realpath"), patch("os.path.expanduser"):
                        with patch("redirect_checker.dictConfig"):
                            result = main(args)

        self.assertEqual(result, EXIT_CODE)
        mock_main_loop.assert_called_with(conf)
        mock_daemonize.assert_called_with()

    def test_main_pidfile(self):
        args = ['1', '-c', '/conf', '-P', '/pidfile']
        conf = Mock(LOOGING={}, EXIT_CODE=EXIT_CODE)

        with patch("redirect_checker.create_pidfile") as mock_create_pidfile:
            with patch("redirect_checker.load_config_from_pyfile", Mock(return_value=conf)):
                with patch("redirect_checker.main_loop") as mock_main_loop:
                    with patch("os.path.realpath"), patch("os.path.expanduser"):
                        with patch("redirect_checker.dictConfig"):
                            result = main(args)

        self.assertEqual(result, EXIT_CODE)
        mock_main_loop.assert_called_with(conf)
        mock_create_pidfile.assert_called_with("/pidfile")
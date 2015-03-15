import unittest
from mock import Mock, patch
from redirect_checker import main, main_loop


class RedirectCheckerTestCase(unittest.TestCase):

    def test_main_loop_network_ok(self):
        config = Mock(WORKER_POOL_SIZE=2, SLEEP=0)
        sleep = Mock(side_effect=KeyboardInterrupt)
        spawner = Mock()

        with patch('redirect_checker.sleep', sleep, create=True):
            with self.assertRaises(KeyboardInterrupt):
                with patch('redirect_checker.spawn_workers', spawner):
                    with patch('redirect_checker.check_network_status', Mock(return_value=True)):
                        main_loop(config)

        spawner_calls = spawner.mock_calls
        assert len(spawner_calls) == 1

    def test_main_loop_network_ok_without_spawn(self):
        config = Mock(WORKER_POOL_SIZE=0, SLEEP=0)
        sleep = Mock(side_effect=KeyboardInterrupt)

        with patch('redirect_checker.sleep', sleep, create=True):
            with self.assertRaises(KeyboardInterrupt):
                with patch('redirect_checker.spawn_workers') as spawner:
                    with patch('redirect_checker.check_network_status', Mock(return_value=True)):
                        main_loop(config)

        spawner_calls = spawner.mock_calls
        assert len(spawner_calls) == 0

    def test_main_loop_network_down(self):
        config = Mock(WORKER_POOL_SIZE=0, SLEEP=0)
        sleep = Mock(side_effect=KeyboardInterrupt)
        children = [Mock(), Mock(), Mock()]

        with patch('redirect_checker.sleep', sleep, create=True):
            with self.assertRaises(KeyboardInterrupt):
                with patch('redirect_checker.active_children', Mock(return_value=children)):
                    with patch('redirect_checker.check_network_status', Mock(return_value=False)):
                        main_loop(config)

        for child in children:
            child.terminate.assert_called_once_with()
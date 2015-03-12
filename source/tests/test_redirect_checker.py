import unittest
from mock import Mock, patch
import redirect_checker


class RedirectCheckerTestCase(unittest.TestCase):

    def test_main_loop_network_down(self):
        config = Mock(WORKER_POOL_SIZE=0, SLEEP=0)
        sleep = Mock(side_effect=KeyboardInterrupt)
        logger = Mock()

        with patch('redirect_checker.logger', logger, create=True):
            with patch('redirect_checker.sleep', sleep, create=True):
                with self.assertRaises(KeyboardInterrupt):
                    with patch('redirect_checker.check_network_status', Mock(return_value=False)):
                        redirect_checker.main_loop(config)

        logger.critical.assert_called_once_with("Network is down. stopping workers")

    def test_main_loop_network_ok(self):
        config = Mock(WORKER_POOL_SIZE=2, SLEEP=0)
        sleep = Mock(side_effect=KeyboardInterrupt)
        spawner = Mock()
        logger = Mock()

        with patch('redirect_checker.logger', logger, create=True):
            with patch('redirect_checker.sleep', sleep, create=True):
                with self.assertRaises(KeyboardInterrupt):
                    with patch('redirect_checker.spawn_workers', spawner):
                        with patch('redirect_checker.check_network_status', Mock(return_value=True)):
                            redirect_checker.main_loop(config)

        logger.info.assert_called_with("Spawning 2 workers")

        logger_calls = logger.info.mock_calls
        assert len(logger_calls) == 2

        spawner_calls = spawner.mock_calls
        assert len(spawner_calls) == 1
        assert spawner_calls[0][2]['num'] == 2

    def test_main_loop_network_ok_without_spawn(self):
        config = Mock(WORKER_POOL_SIZE=0, SLEEP=0)
        sleep = Mock(side_effect=KeyboardInterrupt)
        spawner = Mock()
        logger = Mock()

        with patch('redirect_checker.logger', logger, create=True):
            with patch('redirect_checker.sleep', sleep, create=True):
                with self.assertRaises(KeyboardInterrupt):
                    with patch('redirect_checker.spawn_workers', spawner):
                        with patch('redirect_checker.check_network_status', Mock(return_value=True)):
                            redirect_checker.main_loop(config)

        spawner_calls = spawner.mock_calls
        assert len(spawner_calls) == 0

        logger_calls = logger.mock_calls
        assert len(logger_calls) == 1
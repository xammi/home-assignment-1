__author__ = 'max'

import unittest
from mock import Mock, patch
from lib.worker import *


DEFAULT_URL = 'test'
TEST_STRING = 'test'
TEST_ID = '123'
URL_ID = 2

class Task:
    def __init__(self, task_id, data):
        self.task_id = task_id
        self.data = data


class WorkerTestCase(unittest.TestCase):

    def test_get_redirect_history_from_task_ok(self):
        redirect_history = [[], [], []]
        init_data = {
            'url': DEFAULT_URL,
            'url_id': URL_ID
        }
        final_data = {
            'url_id': URL_ID,
            'result': redirect_history,
            'check_type': 'normal'
        }

        task = Task(1, init_data)
        with patch('lib.worker.get_redirect_history', return_value=redirect_history):
            result = get_redirect_history_from_task(task, 1)

        self.assertEqual(result, (False, final_data))

    def test_get_redirect_history_from_task_error(self):
        redirect_history = [['ERROR'], [], []]
        init_data = {
            'url': DEFAULT_URL,
            'url_id': URL_ID
        }
        final_data = {
            'url': DEFAULT_URL,
            'url_id': URL_ID,
            'recheck': True
        }

        task = Task(1, init_data)
        with patch('lib.worker.get_redirect_history', return_value=redirect_history):
            result = get_redirect_history_from_task(task, 1)

        self.assertEqual(result, (True, final_data))

    def test_get_redirect_history_from_task_3(self):
        redirect_history = [[], [], []]
        init_data = {
            'url': DEFAULT_URL,
            'url_id': URL_ID,
            'suspicious': 'suspicious'
        }
        final_data = {
            "url_id": URL_ID,
            "result": redirect_history,
            "check_type": "normal",
            'suspicious': 'suspicious'
        }

        task = Task(1, init_data)

        with patch('lib.worker.get_redirect_history', return_value=redirect_history):
            result = get_redirect_history_from_task(task, 1)
        self.assertEqual(result, (False, final_data))


    def test_worker_ack(self):
        config = Mock()
        task = Mock()
        task.meta = Mock(return_value={'pri': TEST_STRING})
        tube = Mock()
        tube.take.return_value = task
        tube.opt = {'tube': TEST_STRING}
        get_tube = Mock(return_value=tube)
        get_redirect_history_from_task = Mock(return_value=(Mock(), Mock()))
        path_exists = Mock(side_effect=[True, False])
        with patch('lib.worker.get_tube', get_tube):
            with patch('lib.worker.get_redirect_history_from_task', get_redirect_history_from_task):
                with patch('lib.worker.os.path.exists',  path_exists):
                    worker(config, TEST_ID)

        task.ack.assert_called_one_with()

    def test_worker_task_none(self):
        config = Mock()
        tube = Mock()
        tube.take.return_value = None
        tube.opt = {'tube': TEST_STRING}
        get_tube = Mock(return_value=tube)
        path_exists = Mock(side_effect=[True, False])
        with patch('lib.worker.get_tube', get_tube):
                with patch('lib.worker.os.path.exists', path_exists):
                    worker(config, TEST_ID)

        path_exists.assert_called_one_with(TEST_ID)

    def test_worker_result_none(self):
        config = Mock()
        task = Mock()
        tube = Mock()
        tube.take.return_value = task
        tube.opt = {'tube': TEST_STRING}
        get_tube = Mock(return_value=tube)
        get_redirect_history_from_task = Mock(return_value=None)
        path_exists = Mock(side_effect=[True, False])
        with patch('lib.worker.get_tube', get_tube):
            with patch('lib.worker.get_redirect_history_from_task', get_redirect_history_from_task):
                with patch('lib.worker.os.path.exists',  path_exists):
                    worker(config, TEST_ID)

        task.ack.assert_called_one_with()

    def test_worker_is_input_none(self):
        config = Mock()
        task = Mock()
        tube = Mock()
        tube.take.return_value = task
        tube.opt = {'tube': TEST_STRING}
        get_tube = Mock(return_value=tube)
        get_redirect_history_from_task = Mock(return_value=(None, Mock()))
        path_exists = Mock(side_effect=[True, False])
        with patch('lib.worker.get_tube', get_tube):
            with patch('lib.worker.get_redirect_history_from_task', get_redirect_history_from_task):
                with patch('lib.worker.os.path.exists',  path_exists):
                    worker(config, TEST_ID)

        task.ack.assert_called_one_with()

    def test_worker_exception(self):
        config = Mock()
        task = Mock()
        task.ack.side_effect = DatabaseError
        tube = Mock()
        tube.take.return_value = task
        tube.opt = {'tube': TEST_STRING}
        get_tube = Mock(return_value=tube)
        get_redirect_history_from_task = Mock(return_value=(None, Mock()))
        path_exists = Mock(side_effect=[True, False])
        logger = Mock()
        with patch('lib.worker.get_tube', get_tube):
            with patch('lib.worker.get_redirect_history_from_task', get_redirect_history_from_task):
                with patch('lib.worker.os.path.exists',  path_exists):
                    with patch('lib.worker.logger', logger):
                            worker(config, TEST_ID)

        logger.eexception.assert_called_one_with()
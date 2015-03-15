__author__ = 'max'

import unittest
from mock import Mock, patch
from lib.worker import get_redirect_history_from_task, worker

DEFAULT_URL = 'http://myurl.com:8080/folder/file.exe'


class Task:
    def __init__(self, task_id, data):
        self.task_id = task_id
        self.data = data


class WorkerTestCase(unittest.TestCase):

    def test_get_redirect_history_from_task_ok(self):
        redirect_history = [[], [], []]
        init_data = {'url': DEFAULT_URL, 'url_id': 2}
        final_data = {'url_id': 2, 'result': redirect_history, 'check_type': 'normal'}

        task = Task(1, init_data)
        with patch('lib.worker.get_redirect_history', return_value=redirect_history):
            result = get_redirect_history_from_task(task, 1)

        self.assertEqual(result, (False, final_data))

    def test_get_redirect_history_from_task_error(self):
        redirect_history = [['ERROR'], [], []]
        init_data = {'url': DEFAULT_URL, 'url_id': 2}
        final_data = {'url': DEFAULT_URL, 'url_id': 2, 'recheck': True}

        task = Task(1, init_data)
        with patch('lib.worker.get_redirect_history', return_value=redirect_history):
            result = get_redirect_history_from_task(task, 1)

        self.assertEqual(result, (True, final_data))
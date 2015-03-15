__author__ = 'max'

import unittest
from mock import Mock, patch
from lib.worker import get_redirect_history_from_task, worker

DEFAULT_URL = 'http://myurl.com:8080/folder/file.exe'


class Task:
    def __init__(self, task_id):
        self.task_id = task_id


class WorkerTestCase(unittest.TestCase):
    def test_get_redirect_history_from_task(self):
        task = Task(1)
        task.data = {'url': DEFAULT_URL, 'not_recheck': 'not_recheck', 'url_id': 2}
        final_data = {'url': DEFAULT_URL, 'not_recheck': 'not_recheck', 'url_id': 2, 'recheck': True}

        with patch('lib.worker.get_redirect_history', return_value=(['ERROR'], [], [])):
            result = get_redirect_history_from_task(task, 1)
        self.assertEqual(result, (True, final_data))
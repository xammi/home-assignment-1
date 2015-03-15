import unittest
from mock import Mock, patch, mock_open
from notification_pusher import *
import notification_pusher


TEST_STRING = 'test'
TEST_ID = 123

class NotificationPusherTestCase(unittest.TestCase):
    def test_create_pidfile_example(self):
        pid = 42
        m_open = mock_open()
        with patch('notification_pusher.open', m_open, create=True):
            with patch('os.getpid', Mock(return_value=pid)):
                create_pidfile('/file/path')

        m_open.assert_called_once_with('/file/path', 'w')
        m_open().write.assert_called_once_with(str(pid))

    def test_notification_worker(self):
        task = Mock()
        task.task_id = TEST_ID
        task.data = {"callback_url": TEST_STRING}

        post = Mock(return_value=Mock())
        task_queue = Mock()

        with patch('requests.post', post):
            notification_worker(task, task_queue)

        task_queue.put.assert_called_with((task, 'ack'))

    def test_notification_worker_exception(self):
        task = Mock()
        task.task_id = TEST_ID
        task.data = {"callback_url": TEST_STRING}

        post = Mock(side_effect=requests.RequestException)
        task_queue = Mock()

        with patch('requests.post', post):
            notification_worker(task, task_queue)

        task_queue.put.assert_called_with((task, 'bury'))

    def test_done_with_processed_tasks(selft):
        task_queue = Mock()
        task_queue.qsize.return_value = 1
        task_queue.get_nowait.return_value = [Mock(), Mock()]
        getattr = Mock()

        with patch('notification_pusher.getattr', getattr, create=True):
            done_with_processed_tasks(task_queue)

        assert getattr.call_count == 1

    def test_done_with_processed_tasks_exception_database(selft):
        task_queue = Mock()
        task_queue.qsize.return_value = 1
        task_queue.get_nowait.return_value = [Mock(), Mock()]
        getattr = Mock(side_effect=tarantool.DatabaseError)
        logger = Mock()

        with patch('notification_pusher.getattr', getattr, create=True):
            with patch('notification_pusher.logger', logger):
                done_with_processed_tasks(task_queue)

        assert logger.exception.called == True

    def test_done_with_processed_tasks_exception_queue_empty(selft):
        task_queue = Mock()
        task_queue.qsize.return_value = 1
        task_queue.get_nowait.side_effect = gevent_queue.Empty
        getattr = Mock()

        with patch('notification_pusher.getattr', getattr, create=True):
            done_with_processed_tasks(task_queue)

        assert getattr.call_count == 0

    def test_stop_handler(self):
        notification_pusher.run_application = True
        notification_pusher.exit_code = 1

        signum = 1
        stop_handler(signum)

        assert notification_pusher.run_application == False
        assert notification_pusher.exit_code == signum + SIGNAL_EXIT_CODE_OFFSET

    def test_main_loop(self):
        config = Mock()
        config.QUEUE_TUBE = TEST_STRING
        config.WORKER_POOL_SIZE = 1

        queue = Mock()
        worker_pool = Mock()
        tarantool_queue = Mock(return_value=queue)
        pool = Mock(return_value=worker_pool)

        notification_pusher.run_application = False

        with patch('notification_pusher.tarantool_queue.Queue', tarantool_queue):
            with patch('notification_pusher.Pool', pool):
                main_loop(config)

        queue.tube.assert_called_with(config.QUEUE_TUBE)
        pool.assert_called_with(config.WORKER_POOL_SIZE)

        assert worker_pool.free_count.call_count == 0






import unittest
from mock import MagicMock, Mock, patch, mock_open, PropertyMock
from notification_pusher import *
import notification_pusher



TEST_STRING = 'test'
TEST_ID = 123
EXIT_CODE = 123

class NotificationPusherTestCase(unittest.TestCase):

    def loop_break(arg1, arg2):
        notification_pusher.run_application = False

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
            with patch('notification_pusher.logger', Mock()):
                notification_worker(task, task_queue)

        task_queue.put.assert_called_with((task, 'bury'))

    def test_notification_woker_requests_post(self):
        task = Mock()
        task.task_id = TEST_ID
        task.data = {"callback_url": TEST_STRING}

        post = Mock(return_value=Mock())
        task_queue = Mock()

        with patch('requests.post', post):
            notification_worker(task, task_queue)

        post.assert_called_with(TEST_STRING, data='{\"id\": 123}')


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

        assert logger.exception.called

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

    def test_main_looprun_application_false(self):
        notification_pusher.run_application = False

        config = Mock()
        config.QUEUE_TUBE = TEST_STRING
        config.WORKER_POOL_SIZE = 1

        queue = Mock()
        worker_pool = Mock()
        tarantool_queue = Mock(return_value=queue)
        pool = Mock(return_value=worker_pool)

        with patch('notification_pusher.tarantool_queue.Queue', tarantool_queue):
            with patch('notification_pusher.Pool', pool):
                main_loop(config)

        queue.tube.assert_called_with(config.QUEUE_TUBE)
        pool.assert_called_with(config.WORKER_POOL_SIZE)

        assert worker_pool.free_count.call_count == 0

    def test_main_loop_run_application_true(self):
        notification_pusher.run_application = True

        config = Mock(SLEEP=0.0)

        tube = Mock()
        queue = Mock()
        queue.tube.return_value = tube
        tube.take.return_value = Mock()

        worker_pool = Mock()
        worker_pool.free_count.return_value = 2

        tarantool_queue = Mock(return_value=queue)

        done_with_processed_tasks = Mock(side_effect=self.loop_break)

        with patch('notification_pusher.tarantool_queue.Queue', tarantool_queue):
            with patch('notification_pusher.Pool', Mock(return_value=worker_pool)):
                with patch('notification_pusher.Greenlet', Mock(return_value=Mock())):
                    with patch('notification_pusher.done_with_processed_tasks', done_with_processed_tasks):
                        main_loop(config)

        assert done_with_processed_tasks.called_with(tarantool_queue)

    def test_install_signal_handlers(self):
        signal = Mock()
        with patch('gevent.signal', signal):
            install_signal_handlers()

        assert signal.call_count == 4

    def test_main_run_application_false(self):
        notification_pusher.run_application = False
        notification_pusher.exit_code = EXIT_CODE
        args = ['description', '-c', '']

        load_config_from_pyfile =  Mock(return_value=Mock())

        with patch('notification_pusher.load_config_from_pyfile', load_config_from_pyfile):
            with patch('notification_pusher.dictConfig'):
                with patch('os.path.realpath'):
                    with patch('os.path.expanduser'):
                        result = main(args)

        assert result == EXIT_CODE

    def test_main_daemonize(self):
        notification_pusher.run_application = False
        notification_pusher.exit_code = EXIT_CODE
        args = ['description', '-c', '/conf', '-d']

        load_config_from_pyfile =  Mock(return_value=Mock())
        daemonize = Mock()

        with patch('notification_pusher.daemonize', daemonize):
            with patch('notification_pusher.load_config_from_pyfile', load_config_from_pyfile):
                with patch('notification_pusher.dictConfig'):
                    main(args)

        daemonize.assert_called_with()


    def test_main_create_pidfile(self):
        notification_pusher.run_application = False
        notification_pusher.exit_code = EXIT_CODE
        args = ['description', '-c', '/conf', '-P', TEST_STRING,]


        load_config_from_pyfile =  Mock(return_value=Mock())
        create_pidfile = Mock()

        with patch('notification_pusher.create_pidfile', create_pidfile):
            with patch('notification_pusher.load_config_from_pyfile', load_config_from_pyfile):
                with patch('notification_pusher.dictConfig'):
                    main(args)

        create_pidfile.assert_called_with(TEST_STRING)

    def test_main_run_application_true(self):
        notification_pusher.run_application = True
        notification_pusher.exit_code = EXIT_CODE
        args = ['description', '-c', '/conf']

        load_config_from_pyfile =  Mock(return_value=Mock())
        main_loop = Mock(side_effect=Exception)

        sleep = Mock(side_effect=self.loop_break)


        with patch('notification_pusher.load_config_from_pyfile', load_config_from_pyfile):
            with patch('notification_pusher.dictConfig'), patch('notification_pusher.logger'):
               with patch("notification_pusher.main_loop", main_loop):
                    with patch('notification_pusher.sleep', sleep):
                        result = main(args)

        assert result == EXIT_CODE










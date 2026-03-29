import unittest
from unittest.mock import MagicMock, patch
from geektime_dl.api.client import GeektimeClient, NetworkError, GeektimeAPIError

class TestRetryLogin(unittest.TestCase):
    @patch('time.sleep', return_value=None)
    def test_relogin_after_5_failures(self, mock_sleep):
        client = GeektimeClient("test_acc", "test_pwd")
        
        # 模拟请求方法
        with patch.object(GeektimeClient, 'login') as mock_login:
            # 准备一个始终抛出异常的模拟响应
            # 注意：GeektimeClient 使用的是 self._session.post 而不是 requests.post
            with patch.object(client._session, 'post') as mock_post:
                mock_post.side_effect = NetworkError("test error")
                
                # 我们直接调用包装后的方法
                try:
                    client.get_course_list()
                except NetworkError:
                    pass
            
            # 验证在尝试中，第 5 次触发了 login
            self.assertTrue(mock_login.called)
            self.assertEqual(mock_login.call_count, 1)

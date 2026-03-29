# coding=utf8
import unittest
from unittest.mock import MagicMock, patch
from geektime_dl.services.course_service import CourseService
from geektime_dl.api.exceptions import CourseNotFoundError

class TestCourseService(unittest.TestCase):
    def setUp(self):
        self.service = CourseService("test_acc", "test_pwd")
        self.service.client = MagicMock()

    def test_login(self):
        self.service.login()
        self.service.client.login.assert_called_once()

    def test_get_course_list(self):
        self.service.get_course_list()
        self.service.client.get_course_list.assert_called_once()

    @patch('geektime_dl.services.course_service.Course.get_or_none')
    def test_get_course_no_cache(self, mock_get_or_none):
        mock_get_or_none.return_value = None
        self.service.client.get_course_intro.return_value = {'id': 1, 'column_title': 'test'}
        self.service.client.get_post_list_of.return_value = []
        
        with patch.object(self.service, '_save_course') as mock_save:
            self.service.get_course(1)
            self.service.client.get_course_intro.assert_called_with(1)
            self.service.client.get_post_list_of.assert_called_with(1)
            mock_save.assert_called_once()

    def test_get_course_not_found(self):
        self.service.client.get_course_intro.side_effect = CourseNotFoundError("not found")
        result = self.service.get_course(999)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()

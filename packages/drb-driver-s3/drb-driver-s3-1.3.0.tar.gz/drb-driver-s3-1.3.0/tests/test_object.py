import io
import os.path
import unittest
from unittest.mock import patch

from drb.core import ParsedPath
from drb.exceptions.core import DrbException

from drb.drivers.aws3 import Auth, DrbS3Service, Requests, DrbS3Object
from tests.utility import S3Obj, DownloadObject, start_mock, stop_mock


class TestSwiftObject(unittest.TestCase):
    service = 's3'
    auth = Auth(service_name=service)
    node = DrbS3Service(auth)
    obj = S3Obj('tests', None)
    with patch.object(Requests, 'list_buckets') as mock:
        mock.return_value = [S3Obj('my_bucket', None),
                             S3Obj('my_bucket_2', None)]
        bucket_1 = node['my_bucket']
    node = DrbS3Object(obj, bucket_1)

    @classmethod
    def setUpClass(cls) -> None:
        start_mock('http://my_tmp_url/')

    @classmethod
    def tearDownClass(cls) -> None:
        stop_mock()

    def test_name(self):
        self.assertEqual('tests', self.node.name)

    def test_children(self):
        self.assertIsNotNone(self.node.children)
        self.assertIsInstance(self.node.children, list)
        self.assertEqual(0, len(self.node.children))

    def test_has_child(self):
        self.assertFalse(self.node.has_child('tests.txt'))
        self.assertFalse(self.node.has_child())
        self.assertFalse(self.node.has_child('test.txt', 'ns'))

    def test_attributes(self):
        self.assertIsNotNone(self.node.attributes)
        self.assertEqual(2, len(self.node.attributes))

    def test_get_attribute(self):
        for attr in self.node.attributes:
            self.assertIsNotNone(self.node.get_attribute(attr[0]))
            self.assertIsNotNone(self.node @ attr[0])
        with self.assertRaises(DrbException):
            self.node.get_attribute('wrong_name')
        with self.assertRaises(KeyError):
            self.node.get_attribute(self.node.attributes[0], 'namespace')

    def test_parent(self):
        self.assertEqual(self.bucket_1, self.node.parent)

    def test_path(self):
        self.assertEqual(ParsedPath('s3/my_bucket/tests').path,
                         self.node.path.path)

    @patch.object(Requests, 'get_obj',
                  return_value=DownloadObject('This is for testing.'))
    def test_impl(self, mock):
        self.assertFalse(self.node.has_impl(DrbException))
        self.assertTrue(self.node.has_impl(io.BytesIO))
        with self.assertRaises(DrbException):
            self.node.get_impl(DrbException)
        with self.node.get_impl(io.BytesIO) as stream:
            self.assertEqual('This is for testing.',
                             stream.read())
        with self.node.get_impl(io.BytesIO) as stream:
            self.assertEqual('Th',
                             stream.read(2))
            self.assertEqual('is i',
                             stream.read(4))
            self.assertEqual(stream.tell(), 6)
        with self.node.get_impl(io.BytesIO) as stream:
            self.assertEqual(stream.seek(10), 10)
            self.assertEqual(stream.seek(1, io.SEEK_CUR), 11)
            self.assertEqual(' te', stream.read().decode()[:3])
            self.assertEqual(stream.tell(), len('This is for testing.'))

    @patch.object(Requests, 'get_temp_url',
                  return_value='http://my_tmp_url/')
    def test_tmp_url(self, mock):
        with self.node.get_impl(io.BytesIO, temp_url=True) as stream:
            self.assertEqual('This is for testing.',
                             stream.read().decode())

    def test_name_space_uri(self):
        self.assertIsNone(self.node.namespace_uri)

    def test_value(self):
        self.assertIsNone(self.node.value)

    def test_auth(self):
        self.assertEqual(self.auth, self.node.get_auth())

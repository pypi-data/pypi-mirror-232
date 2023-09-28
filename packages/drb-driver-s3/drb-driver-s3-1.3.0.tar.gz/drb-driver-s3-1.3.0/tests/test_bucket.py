import os.path
import unittest
from unittest.mock import patch

from drb.core import ParsedPath
from drb.exceptions.core import DrbException

from drb.drivers.aws3 import Auth, DrbS3Service, Requests
from tests.utility import S3Obj


class TestSwiftBucket(unittest.TestCase):
    service = 's3'
    auth = Auth(service_name=service)
    node = DrbS3Service(auth)
    bucket_with_obj = S3Obj('my_bucket', None)
    bucket_no_obj = S3Obj('my_bucket_2', None)
    with patch.object(Requests, 'list_buckets') as mock:
        mock.return_value = [S3Obj('my_bucket', None),
                             S3Obj('my_bucket_2', None)]
        bucket_1 = node['my_bucket']
        bucket_2 = node['my_bucket_2']
        bucket_2._children = []

    @patch.object(Requests, 'list_buckets',
                  return_value=[bucket_no_obj, bucket_with_obj])
    def test_name(self, mock_children):
        self.assertEqual('my_bucket', self.node['my_bucket'].name)
        self.assertEqual('my_bucket_2', self.node['my_bucket_2'].name)

    @patch.object(Requests, 'list_objects',
                  return_value=[S3Obj('tests', bucket_1)])
    def test_children(self, mock_children):
        self.assertIsNotNone(self.node['my_bucket'].children)
        self.assertIsInstance(self.node['my_bucket'].children, list)
        self.assertEqual(1, len(self.node['my_bucket'].children))
        self.assertEqual(0, len(self.node['my_bucket_2'].children))

    def test_attributes(self):
        self.assertIsNotNone(self.node['my_bucket'].attributes)
        self.assertEqual(2, len(self.node['my_bucket'].attributes))

    def test_get_attribute(self):
        for attr in self.node['my_bucket'].attributes:
            self.assertIsNotNone(self.node['my_bucket'].get_attribute(attr[0]))
            self.assertIsNotNone(self.node['my_bucket'] @ attr[0])
        with self.assertRaises(DrbException):
            self.node['my_bucket'].get_attribute('wrong_name')
        with self.assertRaises(DrbException):
            self.node['my_bucket'] @ 'wrong_name'
        with self.assertRaises(KeyError):
            self.node['my_bucket'].get_attribute(
                self.node['my_bucket'].attributes[0], 'namespace')

    def test_parent(self):
        self.assertEqual(self.node, self.node['my_bucket'].parent)

    def test_path(self):
        self.assertEqual(ParsedPath('s3/my_bucket').path,
                         self.node['my_bucket'].path.path)

    def test_impl(self):
        self.assertFalse(self.node.has_impl('impl'))
        with self.assertRaises(DrbException):
            self.node.get_impl('impl')

    def test_has_child(self):
        self.assertTrue(self.node['my_bucket'].has_child('tests'))
        self.assertTrue(self.node['my_bucket'].has_child())
        self.assertFalse(self.node['my_bucket'].has_child('not_here'))
        self.assertFalse(self.node['my_bucket'].has_child('my_bucket', 'ns'))
        self.assertFalse(self.node['my_bucket_2'].has_child())

    def test_name_space_uri(self):
        self.assertIsNone(self.node.namespace_uri)

    def test_value(self):
        self.assertIsNone(self.node.value)

    def test_auth(self):
        self.assertEqual(self.auth, self.node.get_auth())

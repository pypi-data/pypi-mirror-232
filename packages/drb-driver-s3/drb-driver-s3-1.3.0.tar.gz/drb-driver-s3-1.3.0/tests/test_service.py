import os.path
import unittest
from unittest.mock import patch

from drb.core import ParsedPath
from drb.exceptions.core import DrbException

from drb.drivers.aws3 import Auth, DrbS3Service, Requests
from tests.utility import S3Obj


class TestSwiftService(unittest.TestCase):
    service = 's3'
    auth = Auth(service_name=service, )
    node = DrbS3Service(auth)
    children = [
        S3Obj('my_bucket_1', node),
        S3Obj('my_bucket_2', node)
    ]

    def test_name(self):
        self.assertEqual('s3', self.node.name)

    def test_eq(self):
        self.assertEqual(self.node, DrbS3Service(self.auth))
        self.assertEqual(self.node.__hash__(),
                         DrbS3Service(self.auth).__hash__())

    @patch.object(Requests, 'list_buckets', return_value=children)
    def test_children(self, mock_children):
        self.assertIsNotNone(self.node.children)
        self.assertIsInstance(self.node.children, list)
        self.assertEqual(2, len(self.node.children))

    @patch.object(Requests, 'list_buckets', return_value=children)
    def test_has_child(self, mock_children):
        self.assertTrue(self.node.has_child('my_bucket_1'))
        self.assertTrue(self.node.has_child())
        self.assertFalse(self.node.has_child('not_here'))
        self.assertFalse(self.node.has_child('my_bucket_1', 'ns'))

    def test_attributes(self):
        self.assertIsNotNone(self.node.attributes)
        self.assertEqual(0, len(self.node.attributes))

    def test_parent(self):
        self.assertIsNone(self.node.parent)

    def test_path(self):
        self.assertEqual(ParsedPath('s3').path, self.node.path.path)

    def test_impl(self):
        self.assertFalse(self.node.has_impl('impl'))
        with self.assertRaises(DrbException):
            self.node.get_impl('impl')

    def test_name_space_uri(self):
        self.assertIsNone(self.node.namespace_uri)

    def test_value(self):
        self.assertIsNone(self.node.value)

    def test_auth(self):
        self.assertEqual(self.auth, self.node.get_auth())

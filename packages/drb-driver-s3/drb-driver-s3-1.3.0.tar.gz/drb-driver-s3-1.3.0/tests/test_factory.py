import unittest

from drb.core import DrbNode
from drb.drivers.http import DrbHttpNode

from drb.drivers.aws3 import S3NodeFactory, Auth, DrbS3Service


class TestSwiftFactory(unittest.TestCase):
    node = None
    auth = None
    storage_url = "https://my.s3/"
    options = {
        'aws_key_id': 'Default',
        'aws_secret_key': 'Default',
    }

    def test_create(self):
        factory = S3NodeFactory()
        auth = Auth(service_name=self.storage_url,
                    aws_access_key_id=self.options['aws_key_id'],
                    aws_secret_access_key=self.options['aws_secret_key'])
        node = DrbS3Service(auth=auth)
        node = factory.create(node)
        self.assertIsInstance(node, (DrbS3Service, DrbNode))

        node = DrbHttpNode(self.storage_url)
        node = factory.create(node)
        self.assertIsInstance(node, (DrbS3Service, DrbNode))

import unittest
import uuid

from drb.core.factory import FactoryLoader
from drb.nodes.logical_node import DrbLogicalNode
from drb.topics.dao import ManagerDao
from drb.topics.topic import TopicCategory

from drb.drivers.aws3 import S3NodeFactory


class TestSwiftSignature(unittest.TestCase):
    s3_id = uuid.UUID('4ab73f92-bbff-11ec-8422-0242ac120002')
    storage_url = "https+s3://my.s3/"
    storage_url2 = "http+s3://my.s3/"
    storage_url3 = "https://my.s2/"
    fc_loader = None
    topic_loader = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.fc_loader = FactoryLoader()
        cls.topic_loader = ManagerDao()

    def test_impl_loading(self):
        factory_name = 'aws3'

        factory = self.fc_loader.get_factory(factory_name)
        self.assertIsNotNone(factory)
        self.assertIsInstance(factory, S3NodeFactory)

        topic = self.topic_loader.get_drb_topic(self.s3_id)
        self.assertIsNotNone(factory)
        self.assertEqual(self.s3_id, topic.id)
        self.assertEqual('Amazon Simple Storage Service', topic.label)
        self.assertIsNone(topic.description)
        self.assertEqual(TopicCategory.CONTAINER, topic.category)
        self.assertEqual(factory_name, topic.factory)

    def test_impl_signatures(self):
        topic = self.topic_loader.get_drb_topic(self.s3_id)

        node = DrbLogicalNode(self.storage_url)
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode(self.storage_url2)
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode(self.storage_url3)
        self.assertFalse(topic.matches(node))

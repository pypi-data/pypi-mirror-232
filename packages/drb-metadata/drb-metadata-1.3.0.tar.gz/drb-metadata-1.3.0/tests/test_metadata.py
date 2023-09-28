import uuid

import os
import unittest
from drb.topics import resolver
from drb.topics.dao import ManagerDao

from drb.metadata import MetadataAddon


class TestMetadataResolver(unittest.TestCase):
    resource_dir = None
    addon = None

    @classmethod
    def setUpClass(cls) -> None:
        test_dir = os.path.join(os.path.dirname(__file__))
        cls.resource_dir = os.path.join(test_dir, 'resources')
        cls.addon = MetadataAddon()

    def test_addon_metadata(self):
        prd = 'S1A_IW_SLC__1SDV_20200801T101915_20200801T101942_033712_' \
              '03E840_2339.SAFE'
        topic, node = resolver.resolve(os.path.join(self.resource_dir, prd))
        self.assertTrue(self.addon.can_apply(topic))
        metadata = self.addon.apply(node)
        self.assertEqual(7, len(metadata.keys()))
        self.assertEqual('Sentinel-1', metadata['platformName'])
        self.assertEqual('SLC', metadata['productType'])

        prd = 'S1A_RF_RAW__0SDH_20140513T012339_20140513T012340_000572_' \
              '000747_31E3.SAFE'
        topic, node = resolver.resolve(os.path.join(self.resource_dir, prd))
        self.assertTrue(self.addon.can_apply(topic))
        metadata = self.addon.apply(node)
        self.assertEqual(8, len(metadata.keys()))
        self.assertEqual('Sentinel-1', metadata['platformName'])
        self.assertEqual('RAW', metadata['productType'])
        self.assertEqual('BAQ_5_BIT',
                         metadata['noiseCompressionType'])

        self.assertFalse(
            self.addon.can_apply(
                ManagerDao().get_drb_topic(
                    uuid.UUID('487b0c70-6199-46de-9e41-4914520e25d9')
                )
            )
        )

    def test_metadata(self):
        prd = 'S1A_IW_SLC__1SDV_20200801T101915_20200801T101942_033712_' \
              '03E840_2339.SAFE'
        path = os.path.join(self.resource_dir, prd)
        file_topic_id = uuid.UUID('99e6ce18-276f-11ec-9621-0242ac130002')
        topic = ManagerDao().get_drb_topic(file_topic_id)
        node = resolver.create(path)
        self.assertTrue(self.addon.can_apply(topic))
        metadata = self.addon.apply(node, topic=topic)
        self.assertEqual(1, len(metadata.keys()))
        self.assertTrue(metadata['isDirectory'])
        metadata = self.addon.apply(node[0], topic=topic)
        self.assertFalse(metadata['isDirectory'])

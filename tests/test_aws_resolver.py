import unittest
from mock import call, Mock, MagicMock

from configbutler.resolvers import AWSResolver

class TestAWSResolver(unittest.TestCase):

    def test_invalid(self):
        undertest = AWSResolver()
        undertest.tags_resolver = Mock()
        undertest.paramstore_resolver = Mock()
        undertest.metadata_resolver = Mock()

        self.assertEqual(undertest.resolve(["blart"], None), None)

        self.assertEqual([], undertest.tags_resolver.mock_calls)

    def test_tags(self):
        undertest = AWSResolver()
        undertest.tags_resolver = Mock()
        undertest.tags_resolver.resolve = MagicMock(return_value="da-tag")

        self.assertEqual(undertest.resolve(["tags", "blart"], None), "da-tag")
        self.assertEqual([call('blart', None)], undertest.tags_resolver.resolve.mock_calls)

    def test_paramstore(self):
        undertest = AWSResolver()
        undertest.paramstore_resolver = Mock()
        undertest.paramstore_resolver.resolve = MagicMock(return_value="da-param")

        self.assertEqual(undertest.resolve(["paramstore", "blart"], None), "da-param")

        self.assertEqual([call('blart', None)], undertest.paramstore_resolver.resolve.mock_calls)

    def test_metadata(self):
        undertest = AWSResolver()
        undertest.metadata_resolver.resolve = MagicMock(return_value="da-metadata")
        self.assertEqual(undertest.resolve(["metadata", "blart"], None), "da-metadata")

        self.assertEqual([call('blart', None)], undertest.metadata_resolver.resolve.mock_calls)

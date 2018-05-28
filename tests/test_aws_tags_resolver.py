import unittest

from ec2_metadata import EC2Metadata
from mock import call, Mock, MagicMock
import mock
import logging

from configbutler.resolvers import AWSTagResolver


logger = logging.getLogger("configbutler")
logging.basicConfig()


class TestAWSTagsResolver(unittest.TestCase):

    @mock.patch("configbutler.resolvers.logger")
    def test_no_tags_retries(self, mock_logger):
        undertest = AWSTagResolver()
        undertest.RETRY_COUNT = 2
        undertest.metadata = mock.create_autospec(EC2Metadata)
        undertest.metadata.instance_id = "i-12345"

        mock_tags = {
            "Tags": []
        }

        undertest.client = Mock()
        undertest.client.describe_tags = MagicMock(return_value=mock_tags)

        self.assertEqual(None, undertest.resolve("blart", dict))

        self.assertEqual([call(Filters=[{'Values': ['i-12345'], 'Name': 'resource-id'}]),
                          call(Filters=[{'Values': ['i-12345'], 'Name': 'resource-id'}])],
                         undertest.client.describe_tags.mock_calls)

        self.assertEqual([call.error('No AWS::tag values found, waiting 1sec to retry.'),
                          call.error('No AWS::tag values found, waiting 2sec to retry.'),
                          call.error('No AWS::tag values found, continuing with no tags.'),
                          call.error("Unable to find AWS::tag named 'blart'")],
                         mock_logger.mock_calls)

    @mock.patch("configbutler.resolvers.logger")
    def test_with_second_retries(self, mock_logger):

        no_tags = {
            "Tags": []
        }

        some_tags = {
            "Tags": [{"Key": "blart", "Value": "bling"}]
        }

        incr_return_values = [no_tags, some_tags]

        def mock_tags_lookup(**args):
            return incr_return_values.pop(0)

        undertest = AWSTagResolver()
        undertest.RETRY_COUNT = 2
        undertest.metadata = mock.create_autospec(EC2Metadata)
        undertest.metadata.instance_id = "i-12345"

        undertest.client = Mock()
        undertest.client.describe_tags = mock_tags_lookup

        self.assertEqual("bling", undertest.resolve("blart", dict))

        # Should be no values left in the array
        self.assertEqual(0, len(incr_return_values))

        self.assertEqual([call.error('No AWS::tag values found, waiting 1sec to retry.')],
                         mock_logger.mock_calls)

    @mock.patch("configbutler.resolvers.logger")
    def test_with_missing_tag(self, mock_logger):
        undertest = AWSTagResolver()
        undertest.RETRY_COUNT = 2
        undertest.metadata = mock.create_autospec(EC2Metadata)
        undertest.metadata.instance_id = "i-12345"

        mock_tags = {
            "Tags": [{"Key": "aKey", "Value": "aValue"}]
        }

        undertest.client = Mock()
        undertest.client.describe_tags = MagicMock(return_value=mock_tags)

        self.assertEqual(None, undertest.resolve("blart", dict))

        self.assertEqual([call(Filters=[{'Values': ['i-12345'], 'Name': 'resource-id'}])],
                         undertest.client.describe_tags.mock_calls)

        self.assertEqual([call.error("Unable to find AWS::tag named 'blart'")],
                         mock_logger.mock_calls)

    @mock.patch("configbutler.resolvers.logger")
    def test_with_actual_tag(self, mock_logger):
        undertest = AWSTagResolver()
        undertest.RETRY_COUNT = 2
        undertest.metadata = mock.create_autospec(EC2Metadata)
        undertest.metadata.instance_id = "i-12345"

        mock_tags = {
            "Tags": [{"Key": "blart", "Value": "bling"}]
        }

        undertest.client = Mock()
        undertest.client.describe_tags = MagicMock(return_value=mock_tags)

        self.assertEqual("bling", undertest.resolve("blart", dict))

        self.assertEqual([call(Filters=[{'Values': ['i-12345'], 'Name': 'resource-id'}])],
                         undertest.client.describe_tags.mock_calls)

        self.assertEqual([],
                         mock_logger.mock_calls)

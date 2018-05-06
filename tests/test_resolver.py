import unittest

from configbutler.resolvers import AWSInstanceMetadataResolver


class MockEC2Metadata(object):

    account_id = "account_id"
    ami_id = "ami_id"
    ami_launch_index = "ami_launch_index"
    availability_zone = "availability_zone"
    iam_info = "iam_info"
    instance_action = "instance_action"
    instance_id = "instance_id"
    instance_profile_arn = "instance_profile_arn"
    instance_profile_id = "instance_profile_id"
    instance_type = "instance_type"
    private_hostname = "private_hostname"
    private_ipv4 = "private_ipv4"
    public_hostname = "public_hostname"
    public_ipv4 = "public_ipv4"
    region = "region"
    security_groups = "security_groups"


class TestAWSInstanceMetadataResolver(unittest.TestCase):

    def test_invalid(self):
        undertest = AWSInstanceMetadataResolver()

        self.assertEqual(undertest.resolve(["blart"], dict), None)

    def test_account_id(self):

        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["account_id"], dict), "account_id")

    def test_ami_id(self):

        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["ami_id"], dict), "ami_id")

    def test_ami_launch_index(self):
        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["ami_launch_index"], dict), "ami_launch_index")

    def test_availability_zone(self):
        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["availability_zone"], dict), "availability_zone")

    def test_iam_info(self):
        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["iam_info"], dict), "iam_info")

    def test_instance_action(self):
        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["instance_action"], dict), "instance_action")

    def test_instance_id(self):
        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["instance_id"], dict), "instance_id")

    def test_instance_profile_arn(self):
        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["instance_profile_arn"], dict), "instance_profile_arn")

    def test_instance_profile_id(self):
        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["instance_profile_id"], dict), "instance_profile_id")

    def test_instance_type(self):
        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["instance_type"], dict), "instance_type")

    def test_private_hostname(self):
        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["private_hostname"], dict), "private_hostname")

    def test_private_ipv4(self):
        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["private_ipv4"], dict), "private_ipv4")

    def test_public_hostname(self):
        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["public_hostname"], dict), "public_hostname")

    def test_public_ipv4(self):
        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["public_ipv4"], dict), "public_ipv4")

    def test_region(self):
        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["region"], dict), "region")

    def test_security_groups(self):
        undertest = AWSInstanceMetadataResolver()
        undertest.metadata = MockEC2Metadata()

        self.assertEqual(undertest.resolve(["security_groups"], dict), "security_groups")

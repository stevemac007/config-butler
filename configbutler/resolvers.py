
import logging
import socket
import boto3

from string import Template
from botocore.exceptions import ClientError
from psutil import virtual_memory
from ec2_metadata import EC2Metadata
import multiprocessing

logger = logging.getLogger("configbutler")


class UnsafeSubstitution(Exception):

    def __init__(self, cause):
        super(UnsafeSubstitution, self).__init__(cause)


class BaseResolver(object):

    def __init__(self):
        self.safe_mode = False

    def resolve_embedded(self, string, current_properties):
        template = Template(string)
        try:
            if self.safe_mode:
                value = template.safe_substitute(current_properties)
            else:
                value = template.substitute(current_properties)
        except KeyError as ex:
            raise UnsafeSubstitution(ex)
        return value


class BaseSubResolver(object):

    def lookup_sub_resolver(self, resolver_name):
        pass

    def resolve(self, parts, current_properties):
        sub_resolver = self.lookup_sub_resolver(parts[0])
        if sub_resolver is not None:
            return sub_resolver.resolve(parts[1], current_properties)


class StringResolver(BaseResolver):

    def resolve(self, parts, current_properties):
        return self.resolve_embedded(parts[0], current_properties)


class AWSInstanceMetadataResolver(BaseResolver):

    def __init__(self):
        super(AWSInstanceMetadataResolver, self).__init__()
        self.metadata = None

    def _metadata(self):
        if self.metadata is None:
            self.metadata = EC2Metadata()
        return self.metadata

    def resolve(self, parts, current_properties):

        if parts == "account_id":
            return self._metadata().account_id
        elif parts == "ami_id":
            return self._metadata().ami_id
        elif parts == "ami_launch_index":
            return self._metadata().ami_launch_index
        elif parts == "availability_zone":
            return self._metadata().availability_zone
        elif parts == "iam_info":
            return self._metadata().iam_info
        elif parts == "instance_action":
            return self._metadata().instance_action
        elif parts == "instance_id":
            return self._metadata().instance_id
        elif parts == "instance_profile_arn":
            return self._metadata().instance_profile_arn
        elif parts == "instance_profile_id":
            return self._metadata().instance_profile_id
        elif parts == "instance_type":
            return self._metadata().instance_type
        elif parts == "private_hostname":
            return self._metadata().private_hostname
        elif parts == "private_ipv4":
            return self._metadata().private_ipv4
        elif parts == "public_hostname":
            return self._metadata().public_hostname
        elif parts == "public_ipv4":
            return self._metadata().public_ipv4
        elif parts == "security_groups":
            return self._metadata().security_groups
        elif parts == "region":
            return self._metadata().region
        else:
            logger.error("Unable to resolve AWS instance attribute '{}'".format(parts))


class AWSTagResolver(BaseResolver):

    def __init__(self):
        super(AWSTagResolver, self).__init__()
        self.client = None
        self.tags = None
        self.metadata = None

    def _metadata(self):
        if self.metadata is None:
            self.metadata = EC2Metadata()
        return self.metadata

    def _ec2_client(self):
        if self.client is None:
            self.client = boto3.client('ec2')
        return self.client

    def resolve(self, key, current_properties):

        if self.tags is None:
            response = self._ec2_client().describe_tags(
                Filters=[
                    {
                        'Name': 'resource-id',
                        'Values': [self._metadata().instance_id]
                    },
                ]
            )
            self.tags = response["Tags"]

        return self.lookup_tag(key=self.resolve_embedded(key, current_properties), tags=self.tags)

    @staticmethod
    def lookup_tag(key, tags):
        for tag in tags:
            if tag["Key"] == key:
                return tag["Value"]

        return None


class AWSParamStoreResolver(BaseResolver):

    def __init__(self):
        super(AWSParamStoreResolver, self).__init__()
        self.client = None

    def _ssm_client(self):
        if self.client is None:
            self.client = boto3.client('ssm')
        return self.client

    def resolve(self, key, current_properties):

        param_key = self.resolve_embedded(key, current_properties)

        logger.info("Resolving SSM parameter '{}'".format(param_key))
        try:
            param = self._ssm_client().get_parameter(Name=param_key, WithDecryption=True)
            logger.debug(param)
            return param["Parameter"]["Value"]
        except ClientError as ex:
            logger.error("Unable to SSM:paramstore lookup '{}' - cause {}".format(param_key, ex))


class LocalHostResolver(BaseResolver):

    def __init__(self):
        super(LocalHostResolver, self).__init__()
        self.mem = virtual_memory()

    def resolve(self, key, current_properties):
        if key[0] == "hostname":
            return socket.gethostname()
        elif key[0] == "fqdn":
            return socket.getfqdn()
        elif key[0] == "total_memory":
            return self.mem.total
        elif key[0] == "cpu_count":
            return multiprocessing.cpu_count()
        else:
            logger.error("Unable to resolve host function '{}'".format(key[0]))


class AWSResolver(BaseSubResolver):

    def __init__(self):
        super(AWSResolver, self).__init__()
        self.tags_resolver = AWSTagResolver()
        self.paramstore_resolver = AWSParamStoreResolver()
        self.metadata_resolver = AWSInstanceMetadataResolver()

    def lookup_sub_resolver(self, resolver_name):
        if resolver_name == "tags":
            return self.tags_resolver
        elif resolver_name == "paramstore":
            return self.paramstore_resolver
        elif resolver_name == "metadata":
            return self.metadata_resolver
        else:
            logger.error("Unable to locate AWS sub-resolver '{}'".format(resolver_name))


class MathResolver(BaseResolver):

    def resolve(self, key, current_properties):

        val1 = self.resolve_embedded(key[1], current_properties)
        val2 = self.resolve_embedded(key[2], current_properties)

        if key[0] == "multiply":
            return float(val1) * float(val2)
        elif key[0] == "subtract":
            return float(val1) - float(val2)
        elif key[0] == "add":
            return float(val1) + float(val2)
        elif key[0] == "divide":
            return float(val1) / float(val2)
        else:
            logger.error("Unable to locate math function '{}'".format(key[0]))

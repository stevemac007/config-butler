
import logging
import socket
import boto3

from string import Template
from botocore.exceptions import ClientError
from psutil import virtual_memory
from ec2_metadata import EC2Metadata
import multiprocessing

logger = logging.getLogger("configbutler")


class BaseResolver(object):

    def resolve_embedded(self, string, current_properties):
        template = Template(string)
        return template.substitute(current_properties)


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

    def __init__(self) -> None:
        super().__init__()
        self.metadata = EC2Metadata()

    def resolve(self, parts, current_properties):

        if parts[0] == "account_id":
            return self.metadata.account_id
        elif parts[0] == "ami_id":
            return self.metadata.ami_id
        elif parts[0] == "ami_launch_index":
            return self.metadata.ami_launch_index
        elif parts[0] == "availability_zone":
            return self.metadata.availability_zone
        elif parts[0] == "iam_info":
            return self.metadata.iam_info
        elif parts[0] == "instance_action":
            return self.metadata.instance_action
        elif parts[0] == "instance_id":
            return self.metadata.instance_id
        elif parts[0] == "instance_profile_arn":
            return self.metadata.instance_profile_arn
        elif parts[0] == "instance_profile_id":
            return self.metadata.instance_profile_id
        elif parts[0] == "instance_type":
            return self.metadata.instance_type
        elif parts[0] == "private_hostname":
            return self.metadata.private_hostname
        elif parts[0] == "private_ipv4":
            return self.metadata.private_ipv4
        elif parts[0] == "public_hostname":
            return self.metadata.public_hostname
        elif parts[0] == "public_ipv4":
            return self.metadata.public_ipv4
        elif parts[0] == "security_groups":
            return self.metadata.security_groups
        elif parts[0] == "region":
            return self.metadata.region
        else:
            logger.error("Unable to resolve AWS instance attribute '{}'".format(parts[0]))


class AWSTagResolver(BaseResolver):

    def resolve(self, key, current_properties):
        return "tag:"+self.resolve_embedded(key, current_properties)


class AWSParamStoreResolver(BaseResolver):

    def __init__(self) -> None:
        super().__init__()
        self.client = boto3.client('ssm')

    def resolve(self, key, current_properties):

        param_key = self.resolve_embedded(key, current_properties)

        logger.info("Resolving SSM parameter '{}'".format(param_key))
        try:
            param = self.client.get_parameter(Name=param_key, WithDecryption=True)
            logger.debug(param)
            return param["Parameter"]["Value"]
        except ClientError as ex:
            logger.error("Unable to SSM:paramstore lookup '{}' - cause {}".format(param_key, ex))


class LocalHostResolver(BaseResolver):

    def __init__(self) -> None:
        super().__init__()

        self.mem = virtual_memory()

    def resolve(self, key, current_properties):
        if key[0] == "hostname":
            return socket.gethostname()
        elif key[0] == "total_memory":
            return self.mem.total
        elif key[0] == "cpu_count":
            return multiprocessing.cpu_count()
        else:
            logger.error("Unable to resolve host function '{}'".format(key[0]))


class AWSResolver(BaseSubResolver):

    def lookup_sub_resolver(self, resolver_name):
        if resolver_name == "tags":
            return AWSTagResolver()
        elif resolver_name == "paramstore":
            return AWSParamStoreResolver()
        elif resolver_name == "metadata":
            return AWSInstanceMetadataResolver()
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

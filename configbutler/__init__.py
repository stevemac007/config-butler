from string import Template

import sys
import yaml
import json
import logging
import socket
import argparse

from . import _version
from botocore.exceptions import ClientError
from psutil import virtual_memory
from jinja2 import Environment, FileSystemLoader, select_autoescape
import boto3

client = boto3.client('ssm')

logger = logging.getLogger("configioc")
logging.basicConfig()
# logging.basicConfig(level=logging.INFO)


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


class AWSTagResolver(BaseResolver):

    def resolve(self, key, current_properties):
        return "tag:"+self.resolve_embedded(key, current_properties)


class AWSParamStoreResolver(BaseResolver):

    def resolve(self, key, current_properties):

        param_key = self.resolve_embedded(key, current_properties)

        logger.info("Resolving SSM parameter '{}'".format(param_key))
        try:
            param = client.get_parameter(Name=param_key, WithDecryption=True)
            logger.debug(param)
            return param["Parameter"]["Value"]
        except ClientError as ex:
            logger.error("Unable to SSM:paramstore lookup '{}' - cause {}".format(param_key, ex))


class LocalHostResolver(BaseResolver):

    mem = virtual_memory()

    def resolve(self, key, current_properties):
        if key[0] == "hostname":
            return socket.gethostname()
        elif key[0] == "total_memory":
            return self.mem.total
        else:
            logger.error("Unable to resolve host function '{}'".format(key[0]))


class AWSResolver(BaseSubResolver):

    def lookup_sub_resolver(self, resolver_name):
        if resolver_name == "tags":
            return AWSTagResolver()
        elif resolver_name == "paramstore":
            return AWSParamStoreResolver()
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


def lookup_resolver(resolver_name):

    if resolver_name == 'string':
        return StringResolver()
    elif resolver_name == 'aws':
        return AWSResolver()
    elif resolver_name == "host":
        return LocalHostResolver()
    elif resolver_name == "math":
        return MathResolver()
    else:
        logger.error("Unable to locate resolver '{}'".format(resolver_name))


def parse_args(args):
    parser = argparse.ArgumentParser(
        prog="configbutler",
        description="Generate configuration files.",
    )

    parser.add_argument('-s', '--show_properties', action="store_true", help='Print the resolved set of properties')
    parser.add_argument('-n', '--dry_run', action="store_true")

    parser.add_argument('--install-service', action="store_true", help="Install configbutler as service to execute on boot.")

    parser.add_argument('folder')
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s {version}'.format(version=_version.__version__))

    return parser.parse_args(args)


def cli(cli_args):
    args = parse_args(cli_args)
    process(args)


def process(args):
    config = yaml.load(open(args.folder, 'r'))

    resolved_properties = dict()

    for key in config['properties']:
        value = config['properties'][key]
        logger.info(key + " - " + value)

        parts = value.split("|")

        resolver = lookup_resolver(parts[0])
        if resolver is not None:
            resolved_value = resolver.resolve(parts[1:], current_properties=resolved_properties)
            resolved_properties[key] = resolved_value

    if args.show_properties:
        print("---------------------")
        print(" Resolved Properties ")
        print("---------------------")
        print(yaml.dump(resolved_properties, default_flow_style=False))

    env = Environment(
        loader=FileSystemLoader('example'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    for file in config['files']:
        logger.debug(file)

        template = Template(file["src"])
        resolved_filename = template.substitute(resolved_properties)

        template = env.get_template(resolved_filename)

        contents = template.render(resolved_properties)
        if args.dry_run:
            print("DRYRUN: Rendering content for '{}'".format(file['dest']))
            print("----------------------")
            print(contents)
            print("----------------------")
            print("")

def main():
    cli_args = sys.argv[1:]
    cli(cli_args)


if __name__ == '__main__':
    main()

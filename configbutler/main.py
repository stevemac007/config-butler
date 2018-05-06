import sys
import yaml
import argparse
from .resolvers import *

from . import _version
from string import Template
from jinja2 import Environment, FileSystemLoader, select_autoescape
import boto3

client = boto3.client('ssm')

logger = logging.getLogger("configioc")
logging.basicConfig()
# logging.basicConfig(level=logging.INFO)


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
        else:
            with open(file['dest'], 'w') as out:
                out.write(contents)


def main():
    cli_args = sys.argv[1:]
    cli(cli_args)


if __name__ == '__main__':
    main()

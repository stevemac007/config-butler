import sys
import os
import yaml
import argparse
import logging
from .resolvers import StringResolver, AWSResolver, LocalHostResolver, MathResolver, UnsafeSubstitution
# from .service import install_service

from . import _version
from string import Template
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger("configbutler")


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
        return None


def parse_args(args):
    parser = argparse.ArgumentParser(
        prog="configbutler",
        description="Generate configuration files.",
    )

    parser.add_argument('-s', '--show_properties', action="store_true", help='Print the resolved set of properties')
    parser.add_argument('-n', '--dry_run', action="store_true", help="Show the output of the generated files.")

    parser.add_argument('--install-service', action="store_true", help="Install configbutler as service to execute on boot.")
    parser.add_argument("-v", "--verbose", dest="verbose_count",
                        action="count", default=0,
                        help="increases log verbosity for each occurrence.")
    parser.add_argument('-o', metavar="output",
                        type=argparse.FileType('w'), default=sys.stdout,
                        help="redirect output to a file")

    parser.add_argument('entrypoint')
    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=_version.__version__))

    return parser.parse_args(args)


def cli(cli_args):

    logging.basicConfig(format='%(name)s (%(levelname)s): %(message)s')
    args = parse_args(cli_args)

    # Sets log level to WARN going more verbose for each new -v.
    logger.setLevel(max(3 - args.verbose_count, 0) * 10)

    try:
        # if args.install_service:
        #     install_service()
        # else:
        process(args)
    except KeyboardInterrupt:
        logger.error('Program interrupted!')
    finally:
        logging.shutdown()


def process(args):

    if os.path.isdir(args.entrypoint):
        for file_name in os.listdir(args.entrypoint):
            child = os.path.join(args.entrypoint, file_name)
            if os.path.isfile(child):
                process_file(args, child)
    else:
        process_file(args, args.entrypoint)


def process_file(args, filename):

    print("Processing configuration {}".format(filename))

    config = yaml.load(open(filename, 'r'))

    resolved_properties = resolve_properties(args, config)
    render_files(args, config, resolved_properties)


def resolve_properties(args, config):

    resolved_properties = dict()
    deferred_properties = list(config['properties'].keys())
    last_size = 0
    safe_mode = False

    logger.debug(config['properties'])

    # We need to try (until we can't) to expand the available variables
    while len(deferred_properties) > 0:

        # Once we have resolved no more properties, we need to do the final pass in safe mode
        if last_size == len(deferred_properties):
            logger.error(deferred_properties)
            safe_mode = True

        last_size = len(deferred_properties)

        for key in deferred_properties:
            value = config['properties'][key]
            logger.info("Processing property - " + key + " = " + value)

            parts = value.split("|")
            logger.debug("Lookup resolver '{}'".format(parts[0]))
            resolver = lookup_resolver(parts[0])

            try:
                if resolver is not None:
                    logger.debug("Resolver found '{}'".format(resolver))
                    resolver.safe_mode = safe_mode
                    resolved_value = resolver.resolve(parts[1:], current_properties=resolved_properties)
                    resolved_properties[key] = resolved_value
                else:
                    logger.error("Unable to locate resolver for '{}'".format(parts[0]))
                    resolved_properties[key] = value

                deferred_properties.remove(key)
            except UnsafeSubstitution as ex:
                logger.info("Resolved properties")
                logger.info(resolved_properties)
                logger.info("Deferring render of {}/{} due to {}".format(key, value, ex))

            logger.debug("Progressively resolved properties {}".format(resolved_properties))

    if args.show_properties:
        print("---------------------")
        print(" Resolved Properties ")
        print("---------------------")
        print(yaml.dump(resolved_properties, default_flow_style=False))

    return resolved_properties


def render_files(args, config, resolved_properties):
    env = Environment(
        loader=FileSystemLoader('/'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    if not config.get('files') is None:
        for file in config['files']:
            logger.info("Processing '{}'".format(file["src"]))
            logger.debug(file)

            template = Template(file["src"])
            resolved_filename = template.safe_substitute(resolved_properties)

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

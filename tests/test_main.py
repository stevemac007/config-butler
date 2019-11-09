import unittest

import configbutler.main


class TestResolverLookup(unittest.TestCase):

    def test_invalid_lookup(self):

        result = configbutler.main.lookup_resolver("blart")
        self.assertEqual(None, result)

    def test_aws_lookup(self):

        result = configbutler.main.lookup_resolver("aws")
        self.assertEqual("<class 'configbutler.resolvers.AWSResolver'>", str(type(result)))

    def test_string_lookup(self):

        result = configbutler.main.lookup_resolver("string")
        self.assertEqual("<class 'configbutler.resolvers.StringResolver'>", str(type(result)))

    def test_math_lookup(self):

        result = configbutler.main.lookup_resolver("math")
        self.assertEqual("<class 'configbutler.resolvers.MathResolver'>", str(type(result)))

    def test_host_lookup(self):

        result = configbutler.main.lookup_resolver("host")
        self.assertEqual("<class 'configbutler.resolvers.LocalHostResolver'>", str(type(result)))


class TestArgsParser(unittest.TestCase):

    def test_default(self):
        """
        Should fail as the 'entrypoint' is mandatory
        :return:
        """
        with self.assertRaises(SystemExit):
            configbutler.main.parse_args([])

    def test_valid_entrypoint(self):
        config = configbutler.main.parse_args(["/tmp"])
        self.assertEqual(False, config.dry_run)
        self.assertEqual("/tmp", config.entrypoint)
        self.assertEqual(False, config.show_properties)
        self.assertEqual(False, config.install_service)


class TestProcess(unittest.TestCase):

    def test_default(self):
        cli_args = ["blart"]
        args = configbutler.main.parse_args(cli_args)

        with self.assertRaises(configbutler.main.ExpectedException) as ex:
            configbutler.main.process(args)

        self.assertEqual("Path not found 'blart'", str(ex.exception))

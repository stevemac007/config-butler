import unittest
import mock
import yaml

from configbutler.main import resolve_properties


class TestAWSInstanceMetadataResolver(unittest.TestCase):

    def test_simple(self):

        args = mock.Mock()

        undertest = """
properties:
    a: string|a
    aa: string|${a}${a}
    ab: string|${a}b
"""
        properties = resolve_properties(args, yaml.load(undertest))

        self.assertEqual(properties["a"], "a")
        self.assertEqual(properties["aa"], "aa")
        self.assertEqual(properties["ab"], "ab")

    def test_unresolved(self):

        args = mock.Mock()

        undertest = """
properties:
    a: string|a
    aa: string|${a}${a}
    ab: string|${a}${b}
"""
        properties = resolve_properties(args, yaml.load(undertest))

        self.assertEqual(properties["a"], "a")
        self.assertEqual(properties["aa"], "aa")
        self.assertEqual(properties["ab"], "a${b}")

    def test_outoforder(self):

        args = mock.Mock()

        undertest = """
properties:
    the: string|the ${end}
    end: string|end
"""
        properties = resolve_properties(args, yaml.load(undertest))

        self.assertEqual(properties["the"], "the end")
        self.assertEqual(properties["end"], "end")

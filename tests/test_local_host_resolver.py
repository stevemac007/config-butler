import unittest

from configbutler.resolvers import LocalHostResolver


class TestLocalHostResolver(unittest.TestCase):

    def test_invalid(self):
        undertest = LocalHostResolver()

        self.assertEqual(undertest.resolve(["invalid"], dict), None)

    # def test_hostname(self):
    #     undertest = LocalHostResolver()
    #
    #     self.assertEqual(undertest.resolve(["hostname"], dict), None)
    #
    # def test_total_memory(self):
    #     undertest = LocalHostResolver()
    #
    #     self.assertEqual(undertest.resolve(["total_memory"], dict), None)
    #
    # def test_cpu_count(self):
    #     undertest = LocalHostResolver()
    #
    #     self.assertEqual(undertest.resolve(["cpu_count"], dict), None)

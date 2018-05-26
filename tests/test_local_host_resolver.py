import unittest
import mock

from configbutler.resolvers import LocalHostResolver


class TestLocalHostResolver(unittest.TestCase):

    def test_invalid(self):
        undertest = LocalHostResolver()

        self.assertEqual(None, undertest.resolve(["invalid"], dict))

    @mock.patch("socket.gethostname")
    def test_hostname(self, mock_gethostname):
        mock_gethostname.return_value = "mock_hostname"
        undertest = LocalHostResolver()

        self.assertEqual("mock_hostname", undertest.resolve(["hostname"], dict))
        mock_gethostname.assert_called_with()

    @mock.patch("socket.getfqdn")
    def test_fqdn(self, mock_getfqdn):
        mock_getfqdn.return_value = "mock_fqdn"
        undertest = LocalHostResolver()

        self.assertEqual("mock_fqdn", undertest.resolve(["fqdn"], dict))
        mock_getfqdn.assert_called_with()

    def test_total_memory(self):
        undertest = LocalHostResolver()
        undertest.mem = mock.Mock()
        undertest.mem.total = 12345

        self.assertEqual(12345, undertest.resolve(["total_memory"], dict))

    @mock.patch("multiprocessing.cpu_count")
    def test_cpu_count(self, mock_cpu_count):
        mock_cpu_count.return_value = 3
        undertest = LocalHostResolver()

        self.assertEqual(3, undertest.resolve(["cpu_count"], dict))
        mock_cpu_count.assert_called_with()

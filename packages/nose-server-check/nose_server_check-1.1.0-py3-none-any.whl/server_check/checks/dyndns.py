"""Check if DynDns IP was updated correctly"""
import logging
import socket
import urllib.request

import server_check.checks.base

MODULE_LOGGER = logging.getLogger(__name__)


class CheckDynDNS(server_check.checks.base.CheckBase):
	"""Class for checking if DynDns IP was updated correctly"""

	def __init__(self, host_names: list[str]):
		"""Create test for checking if DynDns IP where set correctly

		:param host_names: list of host names to check
		"""
		super().__init__()
		self._hostnames = host_names

	def run(self):
		with urllib.request.urlopen("https://v4.ident.me") as data:
			external_ip = data.read().decode("utf8")

		for host_name in self._hostnames:
			MODULE_LOGGER.debug(f"Check ip of {host_name}")
			dns_ip = socket.gethostbyname_ex(host_name)[2][0]
			if dns_ip != external_ip:
				MODULE_LOGGER.warning(msg := f"The IP address of '{host_name}' is wrong! expected: {external_ip} | actual: {dns_ip}")
				self.add_test_result(host_name, False, msg)
			else:
				MODULE_LOGGER.info(msg := f"The IP address of '{host_name}' is correct")
				self.add_test_result(host_name, True, msg)

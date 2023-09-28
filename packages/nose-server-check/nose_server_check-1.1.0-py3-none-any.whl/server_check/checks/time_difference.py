"""Checks if time is synced over all systems."""
import datetime
import logging
import re
import subprocess
import time

import requests

import server_check.checks.base

MODULE_LOGGER = logging.getLogger(__name__)


class CheckTimeDifference(server_check.checks.base.CheckBase):
	"""Check if time is synced over all systems."""

	def __init__(self, ip_addresses: list[str], max_time_difference: float):
		"""Create time difference check.

		:param ip_addresses: list of IP addresses to check
		:param max_time_difference: maximum time difference compared to NTP
		"""
		super().__init__()
		self._ip_addresses = ip_addresses
		self._time_threshold = max_time_difference
		self._local_offset = self._get_local_offset()

	def _get_local_offset(self) -> float:
		"""Get time offset of the local machine.

		:return: time offset in seconds. If positive, the current PC is ahead to the real time
		"""
		try:
			return time.time() - self._get_time_from_ntp()
		except Exception:  # pylint: disable=broad-except
			MODULE_LOGGER.exception("Could not get local offset")
			return 0

	@staticmethod
	def _get_time_from_ntp(time_zone: str = "Europe/Berlin") -> int:
		"""Get current time from world time API.

		:param time_zone: Time zone name
		:return: Current Timestamp
		"""
		response = requests.get(f"http://worldtimeapi.org/api/timezone/{time_zone}", timeout=10)
		return response.json()["unixtime"]

	def run(self):
		"""Check time difference of the given IP addresses compared to the current PC."""

		regex_pattern = r"\d{2}.\d{2}.\d{4} \d{2}.\d{2}.\d{2}"

		for ip_address in self._ip_addresses:
			MODULE_LOGGER.debug(f"Checking time delay of {ip_address}")
			try:
				result = subprocess.check_output(f"net time \\\\{ip_address}").decode("utf-8", errors="ignore")
			except subprocess.CalledProcessError as exc:
				if exc.returncode == 2:
					MODULE_LOGGER.exception(msg := f"{ip_address}: Permission denied!")
					self.add_test_result(ip_address, False, msg)
				else:
					MODULE_LOGGER.exception(msg := f"{ip_address}: Could not get time difference! Exceptions occurred.")
					self.add_test_result(ip_address, False, msg)
				continue
			match = re.search(regex_pattern, result)
			if not match:
				MODULE_LOGGER.error(msg := f"{ip_address}: Could not get time difference! No match.")
				self.add_test_result(ip_address, False, msg)
				continue

			match_result = match.group()
			timestamp = time.mktime(datetime.datetime.strptime(match_result, "%d.%m.%Y %H:%M:%S").timetuple())
			if (time_difference := round(abs(timestamp - time.time() + self._local_offset), 1)) > self._time_threshold:
				MODULE_LOGGER.warning(msg := f"Time difference of '{ip_address}' is to big. Actual: {time_difference}s | Threshold: {self._time_threshold}s")
				self.add_test_result(ip_address, False, msg)
			else:
				MODULE_LOGGER.info(msg := f"Time difference of '{ip_address}' is {time_difference}s")
				self.add_test_result(ip_address, True, msg)

"""Run all checks"""
import datetime
import json
import logging
import os
import pathlib
import threading
import time

import multi_notifier.send_handler
import server_check

import server_check.checks.backup_age
import server_check.checks.base
import server_check.checks.dyndns
import server_check.checks.mail
import server_check.checks.time_difference
import server_check.common

MODULE_LOGGER = logging.getLogger(__name__)


def setup_logger() -> None:
	"""Setup the logger"""
	log_formatter = logging.Formatter("%(asctime)s.%(msecs)03d | %(threadName)s | %(levelname)s | %(name)s:%(lineno)d | %(message)s", datefmt="%Y-%m-%d | %H:%M:%S")
	root_logger = logging.getLogger()
	root_logger.setLevel(logging.DEBUG)
	logging.getLogger("requests").setLevel(logging.WARNING)
	logging.getLogger("urllib3").setLevel(logging.WARNING)

	console_handler = logging.StreamHandler()
	console_handler.setFormatter(log_formatter)
	console_handler.setLevel(logging.DEBUG)
	root_logger.addHandler(console_handler)

	log_path = pathlib.Path(__file__).parent / "logs" / datetime.datetime.now().strftime("%Y-%m-%d_%H-%M_check.log")
	if not log_path.parent.is_dir():
		os.makedirs(log_path.parent)

	file_handler = logging.FileHandler(log_path, encoding="utf-8")
	file_handler.setFormatter(log_formatter)
	file_handler.setLevel(logging.DEBUG)
	root_logger.addHandler(file_handler)


class TestRunner:
	"""Class for running all tests."""

	def __init__(self) -> None:
		"""Init test runner."""
		MODULE_LOGGER.info(f"Current server_check version = {server_check.__version__}")
		self.__config = self.get_config(pathlib.Path(__file__).absolute().parent.parent / "config.json")
		self.notifier = multi_notifier.send_handler.SendHandler(self.__config)

		self.test_cases = []
		self.__add_testcases_from_config()

		self.test_results: dict[str, [server_check.checks.base.TestResult]] | None = None
		self.test_results_previous: dict[str, [server_check.checks.base.TestResult]] | None = None

		self.last_run_file_path = pathlib.Path(__file__).parent / "last_run.json"
		if self.last_run_file_path.is_file():
			with self.last_run_file_path.open() as last_run_file:
				try:
					last_result = json.load(last_run_file, cls=server_check.common.EnhancedJSONDecoder)
					self.last_run_time = datetime.datetime.fromtimestamp(float(last_result["run_time"]))
					self.test_results_previous = last_result["results"]
				except (ValueError, KeyError, TypeError):
					self.last_run_time = None
					self.test_results_previous = None
		else:
			with open(self.last_run_file_path, "w", encoding="utf-8"):
				pass
			self.last_run_time = None

	def __add_testcases_from_config(self) -> None:
		"""Add all test cases from config to test runner"""

		if "check_backup_age" in self.__config:
			try:
				self.test_cases.append(server_check.checks.backup_age.CheckBackupAge([server_check.checks.backup_age.BackupAgeConfig.from_dict(config) for config in self.__config["check_backup_age"]]))
			except TypeError:
				MODULE_LOGGER.exception("Config is wrong for CheckBackupAge")

		if "check_dyndns" in self.__config:
			try:
				self.test_cases.append(server_check.checks.dyndns.CheckDynDNS(self.__config["check_dyndns"]["hostnames"]))
			except KeyError as exc:
				MODULE_LOGGER.exception(f"Config key '{exc}' is missing for CheckDynDNS")

		if "check_mail" in self.__config:
			try:
				self.test_cases.append(server_check.checks.mail.CheckMail(self.notifier._mail))  # pylint: disable=protected-access
			except KeyError as exc:
				MODULE_LOGGER.exception(f"Config key '{exc}' is missing for CheckMail")

		if "check_time_difference" in self.__config:
			try:
				self.test_cases.append(server_check.checks.time_difference.CheckTimeDifference(self.__config["check_time_difference"]["ip_addresses"], self.__config["check_time_difference"]["max_time_difference"]))
			except KeyError as exc:
				MODULE_LOGGER.exception(f"Config key '{exc}' is missing for CheckTimeDifference")

	@staticmethod
	def get_config(path: pathlib.Path) -> dict:
		"""Load config from json file and return it as dictionary.

		:param path: path of config file
		:return: full config
		"""
		with path.open() as config_file:
			config = json.load(config_file)

		return config

	def run_all_tests(self) -> None:
		"""Run all test in separate threads."""
		test_case_threads = []
		for test_case in self.test_cases:
			test_case_threads.append(threading.Thread(target=test_case.run, name=f"{test_case.name}_Thread", daemon=True))

		for thread in test_case_threads:
			thread.start()

		for thread in test_case_threads:
			thread.join(timeout=600)

		self.test_results = self.__get_all_results()
		self._update_last_run()

	def __get_all_results(self) -> dict[str, list[server_check.checks.base.TestResult]]:
		"""Get all results as dictionary.

		:return: result of all test cases
		"""
		test_results = {}
		for test_case in self.test_cases:
			test_results[test_case.name] = test_case.test_results

		return test_results

	def _update_last_run(self) -> None:
		"""Update last run file."""
		last_run_result = {
			"run_time": str(time.time()),
			"results": self.test_results
		}

		with self.last_run_file_path.open("w") as last_run_file:
			json.dump(last_run_result, last_run_file, cls=server_check.common.EnhancedJSONEncoder, indent=4)

	def __check_previous_result_passed(self, test_case_name: str, result_name: str) -> bool:
		"""Check if test was passed during the last run.

		:param test_case_name: Name of test case / check
		:param result_name: Name of the single result
		:return: True if last run was passed, False if not or could not be checked
		"""
		if not self.test_results_previous:
			return False

		previous_test_result = [prev_result for prev_result in self.test_results_previous.get(test_case_name, []) if prev_result.name == result_name]
		return previous_test_result[0].passed if previous_test_result else False

	def run_all_tests_and_send_result(self) -> None:
		"""Run all tests and send the results."""
		self.run_all_tests()
		all_tests_passed = all((test_case.num_failed_tests == 0 for test_case in self.test_cases))
		send_full_report = self.last_run_time is None or self.last_run_time.date() != datetime.datetime.today().date()
		notification_level = multi_notifier.NotificationLevel.INFO if all_tests_passed else multi_notifier.NotificationLevel.WARNING

		# Create a dict of results which should be sent
		results_to_notify = {}
		for test_case in self.test_cases:
			for result in test_case.test_results:
				if send_full_report or not result.passed or not self.__check_previous_result_passed(test_case.name, result.name):
					if (heading := test_case.get_heading_string()) not in results_to_notify:
						results_to_notify[heading] = []
					results_to_notify[heading].append(result)

		# Create message which should be sent
		message = ""
		for test_case_name, test_case_result in results_to_notify.items():
			if message:
				message += "\n"
			message += f"{test_case_name}\n"
			for result in test_case_result:
				message += f"{result}\n"

		if message:
			self.notifier.send_message(message, notification_level)


def run_all_checks() -> None:
	"""Run all checks."""
	setup_logger()
	test_runner = TestRunner()
	test_runner.run_all_tests_and_send_result()


if __name__ == "__main__":
	run_all_checks()

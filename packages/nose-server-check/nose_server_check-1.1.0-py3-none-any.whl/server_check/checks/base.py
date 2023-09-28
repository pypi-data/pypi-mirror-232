"""Common part for all checks"""
import abc
import dataclasses

import server_check.common


@dataclasses.dataclass
class TestResult:
	"""Data class for defining the structure of a test result"""
	__PASSED_ICON = "\u2705"
	__FAILED_ICON = "\u274c"

	name: str
	passed: bool
	message: str

	def __str__(self) -> str:
		"""Get human-readable string fo

		:return: Human-readable representation of the test result
		"""
		return f"{self.__PASSED_ICON if self.passed else self.__FAILED_ICON} {self.message}"


class CheckBase(abc.ABC):
	"""Base class for all checks"""

	def __init__(self):
		"""Common init."""
		self.name = self.__class__.__name__
		self.test_results: list[TestResult] = []

	@abc.abstractmethod
	def run(self):
		"""Run test"""

	def add_test_result(self, name: str, passed: bool, message: str) -> None:
		"""Add a test result

		:param name: unique name of the test case
		:param passed: True if passed, false if failed
		:param message: Message which describes the test result
		:raises server_check.common.ServerCheckException: if message is not unique
		"""
		if name in [result.name for result in self.test_results]:
			raise server_check.common.ServerCheckException(f"A test result with the name '{name}' was already added! The names must be unique")
		self.test_results.append(TestResult(name, passed, message))

	def get_heading_string(self) -> str:
		"""Get heading of check to use it for a human-readable report.

		:return: Headline for report
		"""
		return f"=== {self.name}: passed {self.num_passed_tests}/{len(self.test_results)} ==="

	@property
	def num_passed_tests(self) -> int:
		"""Get the number of passed tests

		:return: number of passed tests
		"""
		return len([result for result in self.test_results if result.passed])

	@property
	def num_failed_tests(self) -> int:
		"""Get the number of failed tests

		:return: number of failed tests
		"""
		return len([result for result in self.test_results if not result.passed])

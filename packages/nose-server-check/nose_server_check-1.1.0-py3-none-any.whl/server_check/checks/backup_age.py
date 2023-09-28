"""Check if backup is not too old."""
import dataclasses
import glob
import logging
import os
import pathlib
import time

import server_check.checks.base

MODULE_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class BackupAgeConfig:
	"""Define Config for CheckBackupAge"""
	path: pathlib.Path
	warning_days: float

	@classmethod
	def from_dict(cls, config_dict: dict) -> "BackupAgeConfig":
		"""Get BackupAgeConfig from config_dict

		:param config_dict: config as dict -> Every config must have a 'path' and a 'warning_days' key!
		:return: Single config object for CheckBackupAge
		"""
		return cls(pathlib.Path(config_dict["path"]), config_dict["warning_days"])


class CheckBackupAge(server_check.checks.base.CheckBase):
	"""Class for checking if backup age is not too old."""

	def __init__(self, config: list[BackupAgeConfig]) -> None:
		"""Init check for backup age

		:param config: config of check backup age
		:raises server_check.common.ConfigurationException: if config is not correct."""
		super().__init__()
		self.__config = config

	def run(self):
		"""Check backup age by finding the newest file in the configured folders"""
		for check in self.__config:
			MODULE_LOGGER.debug(f"Check backup age of {check.path} with warning days = {check.warning_days}")

			list_of_files = glob.glob(str(check.path / "**/*.*"), recursive=True)
			latest_file_timestamp = os.path.getctime(max(list_of_files, key=os.path.getctime))
			file_age_days = (time.time() - latest_file_timestamp) / 3600 / 24

			if file_age_days > check.warning_days:
				MODULE_LOGGER.warning(msg := f"Backup of folder '{check.path} is {round(file_age_days, 1)}' days old. Maximum is {check.warning_days} days!")
				self.add_test_result(str(check.path), False, msg)
			else:
				MODULE_LOGGER.info(msg := f"Backup of folder '{check.path} is {round(file_age_days, 1)}' days old")
				self.add_test_result(str(check.path), True, msg)

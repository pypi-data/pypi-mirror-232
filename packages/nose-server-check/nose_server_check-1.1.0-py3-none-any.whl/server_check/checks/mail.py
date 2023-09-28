"""Check if mail is working."""
import logging
import time

import multi_notifier.connectors.connector_mail
import multi_notifier.connectors.exceptions

import server_check.checks.base

MODULE_LOGGER = logging.getLogger(__name__)


class CheckMail(server_check.checks.base.CheckBase):
	"""Class for checking if mail is working correctly."""

	def __init__(self, mail: multi_notifier.connectors.connector_mail.Mail) -> None:
		"""Init mail check

		:param mail: Instance for mail access
		"""
		server_check.checks.base.CheckBase.__init__(self)
		self._mail = mail

	def run(self) -> None:
		"""Run the test"""
		MODULE_LOGGER.debug("Start mail test")
		timestamp = str(time.time())
		mail_receiver = "test@seuling.eu"
		MODULE_LOGGER.debug(f"Send test mail to {mail_receiver} with timestamp = {timestamp}")
		self._mail.send_message(mail_receiver, timestamp, "Test from python")

		MODULE_LOGGER.debug("Wait for incoming mail")
		try:
			start_time = time.time()
			self._mail.wait_for_incoming_mail(30, expected_payload=timestamp, sender_address="testmail.seuling@gmx.de")
			MODULE_LOGGER.info(msg := f"Test mail was received in time! (It took {(time.time() - start_time):.1f} s)")
			self.add_test_result(mail_receiver, True, msg)
		except multi_notifier.connectors.exceptions.ConnectorTimeoutException:
			MODULE_LOGGER.warning(msg := "Test mail did not receive in time!")
			self.add_test_result(mail_receiver, False, msg)
		except Exception as exc:  # pylint: disable=broad-except
			MODULE_LOGGER.exception(msg := f"Test mail did not receive in time! Unhandled exception: {exc}")
			self.add_test_result(mail_receiver, False, msg)

		days = 10
		MODULE_LOGGER.info(f"Remove mails which are older than {days} days")
		try:
			self._mail.delete_old_mails(10)
		except multi_notifier.connectors.exceptions.ConnectorException:
			MODULE_LOGGER.exception("Could not delete mails")
		except Exception as exc:  # pylint: disable=broad-except
			MODULE_LOGGER.exception(f"Unhandled exception during deleting old mails. {exc}")

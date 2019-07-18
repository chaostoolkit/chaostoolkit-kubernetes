import logging
import subprocess

from nimble.core import global_constants

_LOGGER = logging.getLogger(__name__)


class ShellUtils(object):
    """Utilities related to linux shell."""

    def __init__(self, username=global_constants.DEFAULT_SERVER_USERNAME,
                 password=global_constants.DEFAULT_SERVER_PASSWORD):
        """

        :param username: Username to be used for login on the remote server. Defaults to `root`.
        :type username: str
        :param password: Password to be used for login on the remote server. Defaults to `root@123`.
        :type password: str
        """
        self._username = username
        self._password = password

    @staticmethod
    def log_guavus_response(guavus_response, log_response=True):
        """Log the `stdout`, `stderr` and/or `status_code` in `execution.log` from the given `guavus_response`.

        :type guavus_response: :class:`nimble.core.entity.GuavusResponse`
        :param log_response: If True, the `stdout`, `stderr` and `status_code` will be logged from the `guavus_response`
            else only the `status_code` will be logged. Defaults to `True`.
        :type log_response: bool
        """
        if log_response:
            if guavus_response.status_code == 0:
                _LOGGER.info("stdout: %s\nstderr: %s\nstatus code: %s" % (
                    guavus_response.stdout, guavus_response.stderr, guavus_response.status_code))
            else:
                _LOGGER.error("stdout: %s\nstderr: %s\nstatus code: %s" % (
                    guavus_response.stdout, guavus_response.stderr, guavus_response.status_code))
        else:
            if guavus_response.status_code == 0:
                _LOGGER.info("status code: %s" % guavus_response.status_code)
            else:
                _LOGGER.error("status code: %s" % guavus_response.status_code)

    @staticmethod
    def execute_shell_command(command, log_response=True):
        """Execute the given `command` on shell.

        :param command: Command that is to be executed on shell.
        :type command: str
        :param log_response: If True, the `stdout`, `stderr` and `status_code` will be logged from the `guavus_response`
            else only the `status_code` will be logged in `execution.log`. Defaults to `True`.
        :type log_response: bool
        :return: Return response of the given shell `command`.
        :rtype: :class:`nimble.core.entity.GuavusResponse`
        """
        _LOGGER.info("Executing command: %s" % command)
        ######### subprocess_obj = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        subprocess_obj = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
                                          encoding="utf-8")
        response_obj = subprocess_obj.communicate()
        ########################
        # guavus_response = GuavusResponse(response_obj[0].strip(), response_obj[1], subprocess_obj.returncode)
        # ShellUtils.log_guavus_response(guavus_response, log_response=log_response)
        # return guavus_response
        return response_obj

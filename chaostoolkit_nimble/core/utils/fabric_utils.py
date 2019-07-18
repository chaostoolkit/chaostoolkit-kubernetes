import logging

# from nimble.core import global_constants
# from nimble.core.entity.guavus_response import GuavusResponse
# from nimble.core.utils.fabric_utils import FabricUtils
from fabric import operations
from fabric.context_managers import hide

_LOGGER = logging.getLogger(__name__)



def run_command_on_remote(command, ip, username, password, command_timeout=None,
                          connection_timeout=120):
    """Run a shell command on a remote server.

    :param command: Command that is to be executed on the shell of the remote server.
    :type command: str
    :param ip: Remote server ip on which command is to be fired.
    :type ip: str
    :param username: Username to be used for login on the remote server.
    :type username: str
    :param password: Password to be used for login on the remote server.
    :type password: str
    :param command_timeout: Time(in seconds) to wait for the given `command` to get executed, after which
        the `CommandTimeout` exception will be raised.
    :type command_timeout: int
    :param connection_timeout: Time(in seconds) to wait for the connection to get established with the remote server,
        after which the `ConnectionTimeout` exception will be raised.
    :type connection_timeout: int
    :return: Return the result of the command being executed on the remote server.
    :rtype: :class:`operations._AttributeString`
    """
    set_fabric_environment(ip, username, password, connection_timeout=connection_timeout)
    with hide("output"):  # pylint: disable=not-context-manager
        ############ return operations.run(command, timeout=command_timeout)
        return operations.run(command, timeout=command_timeout).stdout

def set_fabric_environment(ip, username, password, sudo_password=None,
                           connection_timeout=120):
    """Set the basic fabric environment variables upon which the other fabric utilities will be operated.

    :param ip: Remote server ip on which the action is to be performed.
    :type ip: str
    :param username: Username to be used for login on the remote server.
    :type username: str
    :param password: Password to be used for login on the remote server.
    :type password: str
    :param sudo_password: Sudo password to be used with the comamnd on the remote server.
    :type sudo_password: str
    :param connection_timeout: Time(in seconds) to wait for the connection to get established with the remote server,
        after which the `ConnectionTimeout` exception will be raised.
    :type connection_timeout: int
    """
    operations.env.host_string = ip
    operations.env.user = username
    operations.env.password = password
    operations.env.sudo_password = sudo_password
    operations.env.warn_only = True
    operations.env.abort_on_prompts = True
    operations.env.disable_known_hosts = True
    operations.env.timeout = connection_timeout

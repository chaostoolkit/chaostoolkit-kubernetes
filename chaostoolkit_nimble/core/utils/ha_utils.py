import logging
import random

from chaostoolkit_nimble.core.exceptions.custom_exceptions import ChaosActionFailedError
from logzero import logger
from nimble.core.entity.components import Components
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.shell_utils import ShellUtils

_LOGGER = logging.getLogger(__name__)


def check_process_running(component, process_name=None):
    if not process_name:
        process_name = Components.get_process_name(component)
    logger.info("Checking if process '%s' is running by fetching its process id." % process_name)
    response_list = NodeManager.node_obj.execute_command_on_component(component,
                                                                      ShellUtils.fetch_process_id(process_name),
                                                                      consolidated_success_flag=False)
    return all([response.stdout != "" for response in response_list])


def kill_process(process_name, component, num_of_nodes=None):
    """Kill the process of any particular component

    :param process_name: Name of the process
    :type process_name: str
    :param component: Name of the component
    :type component: str
    """
    node_aliases = []
    for node in NodeManager.node_obj.nodes_by_type[component]:
        node_aliases.append(node.name)
    if num_of_nodes:
        node_aliases = random.sample(node_aliases, int(num_of_nodes))
    command = ShellUtils.kill_process_by_name(process_name)
    response_list = []
    for node_alias in node_aliases:
        logger.debug("Killing process '%s' on node '%s'" % (process_name, node_alias))
        response = NodeManager.node_obj.execute_command_on_node(node_alias, command)
        if "kill -9 " not in response.stdout:
            raise ChaosActionFailedError("Could not kill process '%s' on node '%s'" % (process_name, node_alias))
        response_list.append(response)
    return str(response_list)

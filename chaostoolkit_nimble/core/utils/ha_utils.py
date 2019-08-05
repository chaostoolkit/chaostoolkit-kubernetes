import logging
import random

from logzero import logger
from nimble.core.entity.components import Components
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.shell_utils import ShellUtils

_LOGGER = logging.getLogger(__name__)

# node_obj = __import__('nimble.core.entity.node_manager').NodeManager.node_obj
# import __builtin__
logger.info("Helooooooooo")


# node_obj = NodeManager.node_obj

#
# def _check_process(result):
#     process_id = result[0]
#     process_id_after_kill_process = result[1]
#     return process_id == process_id_after_kill_process or process_id_after_kill_process == ''


# def fetch_process_id(component, process_name=None):
#     """Fetch the process id for any particular component.
#
#     :param component: Name of the component.
#     :type component: str
#     :return: List of :class:`nimble.core.entity.guavus_response.GuavusResponse` objects.
#     :rtype: list
#     """
#     if process_name:
#         command = ShellUtils.fetch_process_id(process_name)
#     else:
#         process_name = Components.get_process_name(component)
#         command = ShellUtils.fetch_process_id(process_name)
#     _LOGGER.info("Fetching process id for process '%s' from component: %s" % (process_name, component))
#     response_list = NodeManager.node_obj.execute_command_on_component(component, command,
#                                                                       consolidated_success_flag=False)
#     return response_list


def check_process_running(component, process_name=None):
    if not process_name:
        process_name = Components.get_process_name(component)
    logger.info("Checking if process '%s' is running by fetching its process id." % process_name)
    # logger.debug("NODE_OBJ FROM ha_utils: ----------------:  %s" % NodeManager.node_obj.vip)
    return NodeManager.node_obj.execute_command_on_component(component, ShellUtils.fetch_process_id(process_name),
                                                             consolidated_success_flag=True)


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
        response_list.append(NodeManager.node_obj.execute_command_on_node(node_alias, command))
    return str(response_list)

# # def process_ha(component, process_name=None):
# #     """This function is used to do the process HA of the components at the remote server.
# #
# #     :return: Return object of :class:`nimble.core.entity.guavus_response.GuavusResponse`.
# #     :rtype: :class:`nimble.core.entity.guavus_response.GuavusResponse`
# #     """
# #     failure_reason = ""
# #     kill_process(component, process_name)
# #
# #     try:
# #         check_process(process_id, component)
# #         status_code = 0
# #     except RetryError:
# #         status_code = global_constants.DEFAULT_ERROR_CODE
# #         guavus_response_after_kill = fetch_process_id(component)
# #         process_id_after_kill = guavus_response_after_kill[0].stdout
# #         if process_id == process_id_after_kill:
# #             failure_reason = "Process is not killed for component %s" % component
# #         elif process_id_after_kill == "":
# #             failure_reason = "Process is not UP and running after killed for component: %s" % component
# #
# #     guavus_response[0].status_code = status_code
# #     guavus_response[0].healthcheck_response.failure_reason.append(failure_reason)
# #
# #     return guavus_response
#
#
# @retry(wait_fixed=3000, stop_max_delay=300000, retry_on_result=_check_process)
# def check_process(process_id, component):
#     """ This function is used to check the process is up or not.
#
#     :param process_id: It is the process id before killing the process.
#     :type process_id: int
#     :param component: Name of the component.
#     :type component: str
#     :return: Return the process id of the process before kill and after kill.
#     :rtype: tuple
#     """
#     _LOGGER.info("Running process check for process '%s' on component: %s" % (process_name, component))
#     guavus_response_after_kill = fetch_process_id(component)
#     process_id_after_kill_process = guavus_response_after_kill[0].stdout
#     return process_id, process_id_after_kill_process

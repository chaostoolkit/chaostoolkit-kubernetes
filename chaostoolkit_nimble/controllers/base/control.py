from chaoslib.types import Configuration, \
    Experiment, Secrets, Settings
from logzero import logger

from nimble.core import global_constants
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.shell_utils import ShellUtils


def configure_control(configuration: Configuration = None,
                      secrets: Secrets = None, settings: Settings = None,
                      experiment: Experiment = None):
    """
    Configure the control's global state

    This is called once only per Chaos Toolkit's run and should be used to
    initialize any state your control may require.

    The `settings` are only passed when the control is declared in the
    settings file of the Chaos Toolkit.
    """
    setup_files_base_path = "%s/setup" % global_constants.DEFAULT_LOCAL_TMP_PATH
    testbed_file = ShellUtils.execute_shell_command(
        ShellUtils.find_files_in_directory(setup_files_base_path, file_name_regex="open_nebula_*")).stdout
    component_attributes_file = ShellUtils.execute_shell_command(
        ShellUtils.find_files_in_directory(setup_files_base_path, file_name_regex="component_*")).stdout
    if testbed_file and component_attributes_file:
        NodeManager.initialize(testbed_file, component_attributes_file)
        logger.debug("NODE_OBJ VIP FROM BASE CONTROLLER----------------:  %s" % NodeManager.node_obj.vip)
    else:
        raise Exception("Either testbed or component attributes yaml file not found in chaos!")

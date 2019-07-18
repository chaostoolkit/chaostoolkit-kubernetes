from nimble.core import global_constants
# class UserActions(object):
#     """Actions exposed to the user for data validation."""
#
#     def __init__(self, config_parser, node_obj=NodeManager.node_obj):
#         """
#
#         :type config_parser: :class:`nimble.core.configs.validation_config_parser.ValidationConfigParser`
#         :type node_obj: :class:`nimble.core.entity.nodes.Nodes`
#         """
#         self._logger = logging.getLogger(__name__)
#         self.node_obj = node_obj
#         self.config_parser = config_parser
#         self.file_server_utils = FileServerUtils()
from nimble.core.utils.dynamic_substitution_utils import DynamicSubstitutionUtils
from nimble.core.utils.shell_utils import ShellUtils
from nimble.tests.conftest import OPTIONS_DICT


def run_experiment(experiments_template_path=None):
    experiments_base_path = "%s/tmp/experiments" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
    ShellUtils.execute_shell_command(ShellUtils.remove_and_create_directory(experiments_base_path))
    if not experiments_template_path:
        experiments_path = OPTIONS_DICT["experimentsPath"]
        ShellUtils.execute_shell_command(ShellUtils.copy(experiments_path, experiments_base_path))
    else:
        ShellUtils.execute_shell_command(ShellUtils.copy(experiments_template_path, experiments_base_path))

    experiment_file_response = ShellUtils.execute_shell_command(
        ShellUtils.find_files_in_directory(experiments_base_path))
    for experiment_file in experiment_file_response.stdout.strip().split("\n"):
        DynamicSubstitutionUtils.update_file(experiment_file)
        ShellUtils.execute_shell_command("chaos run %s" % experiment_file)

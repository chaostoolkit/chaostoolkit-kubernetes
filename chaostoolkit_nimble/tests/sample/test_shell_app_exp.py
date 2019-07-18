import logging

import pytest
from nimble.core.entity.components import Components
from nimble.core.utils.dynamic_substitution_utils import DynamicSubstitutionUtils
from nimble.core.utils.multiprocessing_utils import MultiprocessingUtils

from chaostoolkit_nimble.actions.base.flows import user_actions
from chaostoolkit_nimble.actions.sample import sample_application_actions

_LOGGER = logging.getLogger(__name__)


class TestShellAppExp():
    @pytest.fixture(scope="session")
    def multiprocessing_utils(self):
        return MultiprocessingUtils(1)

    @pytest.fixture(scope="session")
    def launch_application_on_remote(self, multiprocessing_utils):
        # NodeManager.node_obj.execute_command_on_node("testautomation-mst-01", "nohup sleep 5m &")
        process_list = multiprocessing_utils.run_method_in_parallel_async(
            sample_application_actions.launch_application())
        yield
        for process in process_list:
            process.terminate()

    # def test_application_ha(self, launch_application_on_remote):
    def test_application_ha(self):
        # ha_utils.process_ha(Components.MANAGEMENT.name, "sleep 5m")
        ################## Templating
        # env = Environment(loader=PackageLoader("chaostoolkit_nimble", "resources/templates/shell_application/"))
        # template = env.get_template('shell_app_exp_template.json')
        # process_name = "sleep 5m"
        # variables = {"component": Components.MANAGEMENT.name,
        #              "process_name": process_name,
        #              "expected_process_id": "",
        #              }
        # # print(template.render(variables))
        # json_string = template.render(variables)
        # experiment_file_path = "%s/process_experiment.json" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
        # response_obj = ShellUtils.execute_shell_command("chaos run %s" % (experiment_file_path))

        ###############Dynamic Substitution#################################################################################
        # experiment_template_file_path = "chaostoolkit_nimble/resources/exp_templates/shell_app/shell_app_exp.json"
        # experiment_file_path = "%s/shell_app_exp.json" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
        # ShellUtils.execute_shell_command("cp %s %s" % (experiment_template_file_path, experiment_file_path))
        # process_name = "sleep 5m"
        # variables = {"rand_dynamic_component": Components.NAMENODE.name,
        #              "rand_dynamic_process_name": process_name,
        #              }
        # # print(template.render(variables))
        # DynamicSubstitutionUtils.add(variables)
        # DynamicSubstitutionUtils.update_file(experiment_file_path)
        # response_obj = ShellUtils.execute_shell_command("chaos run %s" % experiment_file_path)

        ######################### User actions & Dynamic Substitution ###########################################################
        experiments_template_path = "chaostoolkit_nimble/resources/exp_templates/shell_app/shell_app_exp.json"
        variables = {"rand_dynamic_component": Components.NAMENODE.name,
                     "rand_dynamic_process_name": "sleep 5m",
                     }
        DynamicSubstitutionUtils.add(variables)
        user_actions.run_experiment(experiments_template_path)

##########################################################################################################
#         env = Environment(loader=PackageLoader("chaostoolkit_nimble", "resources/templates/shell_application"))
#         template = env.get_template('process_experiment_template.json')
#         variables = {"remote_command_var": "echo Hi",
#                      "remote_ip_var": "192.168.135.59",
#                      "remote_username_var": "root",
#                      "remote_password_var": "guavus@123",
#                      "remote_command_timeout_var": 120,
#                      "remote_connection_timeout_var": 120,
#                      "expected_remote_command_output": "Hi",
#                      "local_command_var": "ls",
#                      "local_command_arguments": "/tmp"
#                      }
#
#         print(template.render(variables))
#


# TestChaosOnApplocation().test_application_ha()

import allure
import pytest
from chaostoolkit_nimble.actions.base.flows import chaos_user_actions
from chaostoolkit_nimble.actions.jio.media_plane_actions import MediaPlaneActions
from nimble.actions.base.regression.config_actions import ConfigActions
from nimble.core.entity.components import Components
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.components.hadoop_utils import HadoopCliUtils
from nimble.core.utils.shell_utils import ShellUtils


class TestJio():
    job_alias = "media_plane"
    job_user = "ambari-qa"
    # hdfs_path = "/tmp/aut_squad_dir/csv"

    # @pytest.fixture(scope="session")
    # def sample_actions(self):
    #     return SampleActions(self.job_alias)

    @pytest.fixture(scope="session")
    def media_plane_actions(self, config_parser):
        return MediaPlaneActions(self.job_alias, config_parser, self.job_user)

    @pytest.fixture(scope="session")
    def hadoop_cli_utils(self):
        return HadoopCliUtils()

    # @pytest.fixture(scope="session")
    # def send_data_to_hdfs(self, user_actions, hadoop_cli_utils):
    #     # hadoop_cli_utils.remove(self.hdfs_path, recursive=True)
    #     # user_actions.send_data_to_hdfs(
    #     #     "modules/platform/validation/aut_squad_test_data/input_output_sources/hdfs/csv/", self.hdfs_path)
    #     # yield
    #     # hadoop_cli_utils.remove(self.hdfs_path, recursive=True)
    #     pass

    @pytest.fixture(scope="session")
    def config_actions(self):
        return ConfigActions()

    @pytest.fixture(scope="session", autouse=True)
    def clean_table(self, media_plane_actions):
        command = "hive -e 'drop table if exists %s.%s'" % (
            media_plane_actions.database_name, media_plane_actions.table_name)
        assert NodeManager.node_obj.execute_command_on_node(media_plane_actions.node_alias,
                                                            ShellUtils.su(self.job_user, command)).status

    def test_validation_on_15min_job_ha(self, config_actions, user_actions, media_plane_actions):
        node_alias = NodeManager.node_obj.get_node_aliases_by_component(Components.MANAGEMENT.name)[0]
        with allure.step('Schedule 15 min job'):
            media_plane_actions.schedule_15_min_job()
        with allure.step('Perform Job HA via chaostoolkit'):
            exp_template_file = "process/exp.json"
            context = {"rand_dynamic_component": Components.MANAGEMENT.name,
                       "rand_dynamic_process_name": "media_plane_microapp1",
                       }
            chaos_user_actions.run_experiment(exp_template_file, context)
        with allure.step('Validate the data'):
            user_actions.validate(media_plane_actions.validate_media_plane, self.job_alias)
            # user_actions.validate(sample_actions.validate_hdfs_to_hdfs_csv, self.job_alias)

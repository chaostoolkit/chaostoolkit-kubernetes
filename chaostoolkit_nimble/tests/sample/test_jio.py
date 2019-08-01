import collections

import allure
import pytest
from chaostoolkit_nimble.actions.base.flows import chaos_user_actions
from chaostoolkit_nimble.actions.jio.media_plane_actions import MediaPlaneActions
from nimble.actions.base.regression.config_actions import ConfigActions
from nimble.core.entity.components import Components
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.components.hadoop_utils import HadoopCliUtils
from nimble.core.utils.fabric_utils import FabricUtils
from nimble.core.utils.shell_utils import ShellUtils


class TestJio():
    job_alias = "media_plane"
    # hdfs_path = "/tmp/aut_squad_dir/csv"
    job_user = "ambari-qa"
    database_name = "network360_volte"
    table_name = "media_plane_table"

    # @pytest.fixture(scope="session")
    # def sample_actions(self):
    #     return SampleActions(self.job_alias)

    @pytest.fixture(scope="session")
    def media_plane_actions(self):
        return MediaPlaneActions(self.job_alias)

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

    @pytest.fixture(scope="session")
    def clean_table(self):
        command = "hive -e 'drop table if exists %s.%s'" % (self.database_name, self.table_name)
        NodeManager.node_obj.execute_command_on_node(
            NodeManager.node_obj.get_node_aliases_by_component(Components.MANAGEMENT.name)[0],
            ShellUtils.su(self.job_user, command))

    def test_validation_on_15min_job_ha(self, config_actions, user_actions, media_plane_actions, clean_table):
        with allure.step('Schedule 15 min job'):
            job_base_directory = "/data/jio_copy/microapp1/"
            database_name = "network360_volte"
            kwargs = collections.OrderedDict()
            kwargs["config_separator"] = "="
            kwargs["location"] = "local"
            kwargs["base_path"] = "%s/conf/MediaPlaneJob.json" % job_base_directory
            kwargs["file_format"] = "json"
            kwargs["components"] = [Components.MANAGEMENT.name]
            kwargs["properties"] = {"mediaPlaneRawInput.type": "csv", "mediaPlaneRawInput.header": "true",
                                    "mediaPlaneRawInput.pathPrefix": "/tmp/partition_date=",
                                    "mediaPlaneRawInput.tableName": "%s.%s" % (self.database_name, self.table_name)}
            config_actions.update_configs(**kwargs)

            job_run_command = "export SPARK_HOME=/usr/hdp/2.6.5.0-292/spark2 && cd %s && nohup sh scripts/media_plane_microapp1.sh &" % (
                job_base_directory)
            # guavus_response = NodeManager.node_obj.execute_command_on_node(
            #     NodeManager.node_obj.get_node_aliases_by_component(Components.MANAGEMENT.name)[0],
            #     ShellUtils.su(self.job_user, job_run_command), pty=False)
            FabricUtils.run_command_on_remote_in_bg(job_run_command, "192.168.134.170", "root",
                                                    "guavus@123")
        with allure.step('Perform Job HA via chaostoolkit'):
            ####### To be decided where to keep all templates -- fileserver could be an option
            template_path = "chaostoolkit_nimble/resources/exp_templates/jio/shell_app_exp.json"
            variables_dict = {"rand_dynamic_component": Components.MANAGEMENT.name,
                              "rand_dynamic_process_name": "media_plane_microapp1",
                              }
            chaos_user_actions.run_experiment(template_path, variables_dict)
        with allure.step('Validate the data'):
            user_actions.validate(media_plane_actions.validate_media_plane, self.job_alias)
            # user_actions.validate(sample_actions.validate_hdfs_to_hdfs_csv, self.job_alias)

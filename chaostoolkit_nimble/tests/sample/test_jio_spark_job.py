import logging

import pytest

from chaostoolkit_nimble.actions.base.flows import chaos_user_actions
from chaostoolkit_nimble.actions.jio.media_plane_actions import MediaPlaneActions
from nimble.core.entity.components import Components
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.shell_utils import ShellUtils

_LOGGER = logging.getLogger(__name__)


@pytest.mark.incremental
class TestJioSparkJob():
    job_alias = "Media_Plane"
    job_user = "ambari-qa"
    job_running_component = Components.MANAGEMENT.name

    @pytest.fixture(scope="session")
    def media_plane_actions(self, config_parser):
        return MediaPlaneActions(self.job_alias, config_parser, job_user=self.job_user)

    @pytest.fixture(scope="session")
    def clean_table(self, media_plane_actions):
        command = "hive -e 'drop table if exists %s.%s'" % (
            media_plane_actions.database_name, media_plane_actions.table_name)
        assert NodeManager.node_obj.execute_command_on_node(media_plane_actions.node_alias,
                                                            ShellUtils.su(self.job_user, command)).status

    @pytest.fixture(scope="session")
    def clean_job_stdout_files(self, media_plane_actions):
        command = "cd %s && rm -rf %s" % (media_plane_actions.job_base_directory, media_plane_actions.job_stdout_file)
        NodeManager.node_obj.execute_command_on_node(media_plane_actions.node_alias,
                                                     ShellUtils.su(self.job_user, command))

    @pytest.fixture
    def schedule_job(self, media_plane_actions, clean_table, clean_job_stdout_files):
        assert media_plane_actions.schedule_15_min_job()

    def test_chaos_on_executor_kill(self, schedule_job):
        exp_template_file = "spark/executor_kill_exp.json"
        context = {"job_name": self.job_alias,
                   "num_of_exec_to_kill": "1",
                   }
        chaos_user_actions.run_experiment(exp_template_file=exp_template_file, context=context)
        # chaos_user_actions.run_experiment(exp_file=OPTIONS_DICT["experimentsPath"])

    def test_chaos_on_driver(self, schedule_job):
        exp_template_file = "spark/driver_kill_exp.json"
        context = {"job_name": self.job_alias,
                   }
        chaos_user_actions.run_experiment(exp_template_file=exp_template_file, context=context)
        # chaos_user_actions.run_experiment(exp_file=OPTIONS_DICT["experimentsPath"])

    def test_chaos_on_driver_and_executor_kill(self, schedule_job):
        exp_template_file = "spark/driver_and_executor_kill_exp.json"
        context = {"job_name": self.job_alias,
                   "num_of_exec_to_kill": "1",
                   }
        chaos_user_actions.run_experiment(exp_template_file=exp_template_file, context=context)
        # chaos_user_actions.run_experiment(exp_file=OPTIONS_DICT["experimentsPath"])

    def test_validation_post_chaos(self, user_actions, media_plane_actions):
        user_actions.validate(media_plane_actions.validate_media_plane, self.job_alias)

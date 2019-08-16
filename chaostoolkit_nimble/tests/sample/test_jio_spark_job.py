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

    def test_schedule_15min_job(self, media_plane_actions, clean_table, clean_job_stdout_files):
        assert media_plane_actions.schedule_15_min_job()

    # def test_is_job_running_on_yarn(self):
    #     hadoop_rest_client_utils = HadoopRestClientUtils()
    #     try:
    #         a = hadoop_rest_client_utils.is_yarn_job_running(self.job_alias)
    #     except RetryError:
    #         _LOGGER.exception("Not able to fetch CDAP query status")
    #
    # def test_kill_active_executors(self):
    #     yarn_job_name = "Media_Plane"
    #     spark_job_name = "Media Plane"
    #     num_of_exec = 1
    #     hadoop_rest_client_utils = HadoopRestClientUtils()
    #     spark_client_utils = SparkRestClientUtils()
    #     try:
    #         application_id = hadoop_rest_client_utils.get_yarn_most_recent_application_id_by_job_name(yarn_job_name,
    #                                                                                                   state=ApplicationState.RUNNING.value)
    #     except RetryError:
    #         raise ChaosActionFailedError("Could not fetch yarn application id for job %s in state %s:" % (
    #             yarn_job_name, ApplicationState.RUNNING.value))
    #     executors = spark_client_utils.get_application_active_executors(application_id)
    #     for i in range(len(executors)):
    #         if executors[i]["id"] == "driver":
    #             executors.pop(i)
    #             break
    #     executors = random.sample(executors, int(num_of_exec))
    #     response_list = []
    #     for executor in executors:
    #         executor_id = executor["id"]
    #         node_hostname_domain = executor["hostPort"].split(":")[0]
    #         logger.debug("Killing executor id %s on node %s" % (executor_id, node_hostname_domain))
    #         response = NodeManager.node_obj.execute_command_on_hostname_domain(node_hostname_domain,
    #                                                                            ShellUtils.kill_process_by_name("spark",
    #                                                                                                            pipe_command='grep -i "executor-id %s"' % executor_id))
    #         if "kill -9 " not in response.stdout:
    #             raise ChaosActionFailedError(
    #                 "Could not kill process with executor id %s on node %s" % (executor_id, node_hostname_domain))
    #         response_list.append(response)
    #     return str(response_list)

    def test_perform_15min_spark_job_ha(self):
        exp_template_file = "spark/executor_kill_exp.json"
        context = {"yarn_job_name": self.job_alias,
                   "num_of_exec_to_kill": "1",
                   }
        chaos_user_actions.run_experiment(exp_template_file=exp_template_file, context=context)
        # chaos_user_actions.run_experiment(exp_file=OPTIONS_DICT["experimentsPath"])

    def test_validation_on_15min_job_ha(self, user_actions, media_plane_actions):
        user_actions.validate(media_plane_actions.validate_media_plane, self.job_alias)

    ############################################# YARN APIs

    # def test_get_all_yarn_jobs(self):
    #     res1 = HadoopRestClientUtils().get_all_yarn_jobs()
    #     a = 1
    #
    # def test_get_all_yarn_jobs_with_state(self):
    #     res2 = HadoopRestClientUtils().get_all_yarn_jobs(state=ApplicationState.FINISHED.value)
    #     a = 1
    #
    # def test_get_yarn_most_recent_application_id_by_job_name(self):
    #     res3 = HadoopRestClientUtils().get_yarn_most_recent_application_id_by_job_name(self.job_alias,
    #                                                                               ApplicationState.FINISHED.value)
    #     a = 1
    #
    # def test_get_yarn_job_details(self):
    #     res4 = HadoopRestClientUtils().get_yarn_job_details(HadoopRestClientUtils().get_yarn_most_recent_application_id_by_job_name(self.job_alias,
    #                                                                               ApplicationState.FINISHED.value))
    #     a = 1
    #
    # def test_get_yarn_job_attempts(self):
    #     res5 = HadoopRestClientUtils().get_yarn_job_attempts(
    #         HadoopRestClientUtils().get_yarn_most_recent_application_id_by_job_name(self.job_alias,
    #                                                                                   ApplicationState.FINISHED.value))
    #     a = 1
    #
    # def test_get_yarn_job_last_attempt_id(self):
    #     rest6 = HadoopRestClientUtils().get_yarn_job_last_attempt_id(
    #         HadoopRestClientUtils().get_yarn_most_recent_application_id_by_job_name(self.job_alias,
    #                                                                                   ApplicationState.FINISHED.value))
    #
    #     a = 1

    ######################################## SPARK APIs

    # def test_get_all_applications(self):
    #     sres1 = SparkRestClientUtils().get_all_applications()
    #     a = 1
    #
    # def test_get_all_applications_with_status(self):
    #     sres1 = SparkRestClientUtils().get_all_applications(status=ApplicationStatus.COMPLETED.value)
    #     a = 1
    #
    # def test_get_application_details(self):
    #     sres2 = SparkRestClientUtils().get_application_details(
    #         HadoopRestClientUtils().get_yarn_most_recent_application_id_by_job_name(self.job_alias,
    #                                                                                 ApplicationState.FINISHED.value))
    #     a = 1
    #
    # def test_get_application_attempts(self):
    #     sres3 = SparkRestClientUtils().get_application_attempts(
    #         HadoopRestClientUtils().get_yarn_most_recent_application_id_by_job_name(self.job_alias,
    #                                                                                 ApplicationState.FINISHED.value))
    #     a = 3
    #
    # def test_get_application_last_attempt_id(self):
    #     sres4 = SparkRestClientUtils().get_application_last_attempt_id(
    #         HadoopRestClientUtils().get_yarn_most_recent_application_id_by_job_name(self.job_alias,
    #                                                                                 ApplicationState.FINISHED.value))
    #     a = 2
    #
    # def test_get_application_all_executors(self):
    #     sres5 = SparkRestClientUtils().get_application_all_executors(
    #         HadoopRestClientUtils().get_yarn_most_recent_application_id_by_job_name(self.job_alias,
    #                                                                                 ApplicationState.FINISHED.value))
    #     a = 3
    #
    # def test_get_application_active_executors(self):
    #     sres6 = SparkRestClientUtils().get_application_active_executors(
    #         HadoopRestClientUtils().get_yarn_most_recent_application_id_by_job_name(self.job_alias,
    #                                                                                 ApplicationState.FINISHED.value))
    #     a = 4

    ######################################## CHAOS  APIs
    # def test_is_job_running_on_yarn(self):
    #     yres1 = yarn_apps_ha_utils.is_job_running_on_yarn(self.job_alias)
    #     a = 3
    #
    # def test_is_job_running_on_spark(self):
    #     ssres1 = spark_apps_ha_utils.is_job_running_on_spark("Media Plane")
    #     a = 2
    #
    # def test_kill_executor(self):
    #     ssres2 = spark_apps_ha_utils.kill_active_executors("Media Plane", num_of_exec=2)
    #     a = 4

    # def test_kill_executor(self):
    #     job_name = self.job_alias
    #     num_of_exec = 1
    #     hadoop_rest_client_utils = HadoopRestClientUtils()
    #     spark_client_utils = SparkRestClientUtils()
    #     application_id = hadoop_rest_client_utils.get_yarn_most_recent_application_id_by_job_name(job_name,
    #                                                                                               state=ApplicationState.KILLED.value)
    #     executors = spark_client_utils.get_application_active_executors(application_id)
    #     for i in range(len(executors)):
    #         if executors[i]["id"] == "driver":
    #             executors.pop(i)
    #             break
    #     executors = random.sample(executors, int(num_of_exec))
    #     response_list = []
    #     for executor in executors:
    #         executor_id = executor["id"]
    #         node_hostname_domain = executor["hostPort"].split(":")[0]
    #         response = NodeManager.node_obj.execute_command_on_hostname_domain(node_hostname_domain,
    #                                                                            ShellUtils.kill_process_by_name("spark",
    #                                                                                                            pipe_command="grep -i '--executor-id %s'" % executor_id))
    #         if "kill -9 " not in response.stdout:
    #             raise ChaosActionFailedError(
    #                 "Could not kill process with executor id '%s' on node '%s'" % (executor_id, node_hostname_domain))
    #         response_list.append(response)
    #     return str(response_list)

    # def test_1(self):
    #     arm = BaseHadoopAdapter().active_resource_manager()
    #     a = 5

    # def test_is_job_running_on_yarn(self):
    #     hadoop_rest_client_utils = HadoopRestClientUtils()
    #     a = hadoop_rest_client_utils.is_yarn_job_running(self.job_alias)
    #     b = 4

    # def test_is_job_running_on_spark(self):
    #     spark_client_utils = SparkRestClientUtils()
    #     c = spark_client_utils.is_job_running("Media Plane")
    #     d = 5

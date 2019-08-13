import random

from logzero import logger

from chaostoolkit_nimble.core.exceptions.custom_exceptions import ChaosActionFailedError
from nimble.core.adapters.hadoop.base_hadoop_adapter import ApplicationState
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.shell_utils import ShellUtils

# spark_client_utils = SparkRestClientUtils()


def is_job_running_on_spark(job_name):
    from nimble.core.utils.components.spark_utils import SparkRestClientUtils
    spark_client_utils = SparkRestClientUtils()
    logger.debug("Checking if job '%s' on spark" % job_name)
    spark_client_utils.is_job_running(job_name)


def kill_active_executors(job_name, num_of_exec=1):
    from nimble.core.utils.components.hadoop_utils import HadoopRestClientUtils
    from nimble.core.utils.components.spark_utils import SparkRestClientUtils
    hadoop_rest_client_utils = HadoopRestClientUtils()
    spark_client_utils = SparkRestClientUtils()
    application_id = hadoop_rest_client_utils.get_yarn_most_recent_application_id_by_job_name(job_name,
                                                                                              state=ApplicationState.RUNNING.value)
    executors = spark_client_utils.get_application_active_executors(application_id)
    for i in range(len(executors)):
        if executors[i]["id"] == "driver":
            executors.pop(i)
            break
    executors = random.sample(executors, int(num_of_exec))
    response_list = []
    for executor in executors:
        executor_id = executor["id"]
        node_hostname_domain = executor["hostPort"].split(":")[0]
        logger.debug("Killing executor id %s on node %s" % (executor_id, node_hostname_domain))
        response = NodeManager.node_obj.execute_command_on_hostname_domain(node_hostname_domain,
                                                                           ShellUtils.kill_process_by_name("spark",
                                                                                                           pipe_command="grep -i '--executor-id %s'" % executor_id))
        if "kill -9 " not in response.stdout:
            raise ChaosActionFailedError(
                "Could not kill process with executor id %s on node %s" % (executor_id, node_hostname_domain))
        response_list.append(response)
    return str(response_list)

# # def kill_executor_on_node(node_alias):
#
# def kill_driver() .
#
#
# create
# its
# template
# also
#
# --------------yarn
#
#
# def get_all_jobs():
#     in nimble
#     "curl -i -X GET http://192.168.134.192:8088/ws/v1/cluster/apps/"
#
#
# def get_all_jobs_with_state(state):
#     in nimble
#     "curl -i -X GET http://192.168.134.192:8088/ws/v1/cluster/apps/?state=RUNNING"
#
#
# def get_application_id():
#     in nimble
#
#
# def get_job_details():
#     in nimble
#     "curl -i -X GET http://192.168.134.192:8088/ws/v1/cluster/apps/application_1563363670071_0206"
#
#
# def get_job_elapsed_time():
#
#
# -------------------- spark
#
#
# def get_all_jobs():
#     in nimble
#     "curl -i -X GET http://testautomation-mgt-01.cloud.in.guavus.com:18081/api/v1/applications/"
#     X
#
#
# def get_job_details():
#     in nimble
#     "curl -i -X GET http://testautomation-mgt-01.cloud.in.guavus.com:18081/api/v1/applications/application_1563363670071_0214"
#
#
# def get_job_attempt_ids():
#     in nimble
#
#
# def get_job_executors():
#     "curl -i -X GET http://testautomation-mgt-01.cloud.in.guavus.com:18081/api/v1/applications/application_1563363670071_0214/1/executors/"
#     in nimble
#
#
# handlings
# for kerberos
#     improve
# logging
# docstrings
# pending
# things

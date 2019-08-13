from logzero import logger


# hadoop_rest_client_utils = HadoopRestClientUtils()


def is_job_running_on_yarn(job_name):
    from nimble.core.utils.components.hadoop_utils import HadoopRestClientUtils
    hadoop_rest_client_utils = HadoopRestClientUtils()
    logger.debug("Checking if job '%s' on yarn" % job_name)
    return hadoop_rest_client_utils.is_yarn_job_running(job_name)

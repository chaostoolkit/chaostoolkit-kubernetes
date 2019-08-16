from logzero import logger
from retrying import RetryError

from nimble.core.utils.components.hadoop_utils import HadoopRestClientUtils


def is_job_running_on_yarn(job_name):
    hadoop_rest_client_utils = HadoopRestClientUtils()
    logger.debug("Checking if job '%s' on yarn" % job_name)
    try:
        return hadoop_rest_client_utils.is_yarn_job_running(job_name=job_name)
    except RetryError:
        logger.info("Not able to fetch yarn job status.")
        return False

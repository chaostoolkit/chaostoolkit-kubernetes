from chaoslib.types import Experiment, Configuration, Secrets, Activity, Run, Journal
from logzero import logger

from chaostoolkit_nimble.controllers.base import control
from nimble.core.utils.components.hadoop_utils import HadoopRestClientUtils
from nimble.core.utils.date_utils import DateUtils, Timezone

control.configure_control()
APPLICATION_ID = None


def after_activity_control(context: Activity, state: Run,
                           configuration: Configuration = None,
                           secrets: Secrets = None, **kwargs):
    """
    after-control of the activity's execution

    Called by the Chaos Toolkit before the activity is applied. The result of
    the execution is passed as `state`. See
    https://docs.chaostoolkit.org/reference/api/journal/#run for more
    information.
    """
    logger.debug("----------------STATE AFTER ACTIVITY:  %s" % state)


def before_method_control(context: Experiment,
                          configuration: Configuration = None,
                          secrets: Secrets = None, **kwargs):
    """
    before-control of the method's execution

    Called by the Chaos Toolkit before the activities of the method are
    applied.
    """
    logger.debug("----------------CONFIGURATION BEFORE METHOD:  %s" % configuration)


def after_method_control(context: Experiment,
                         configuration: Configuration = None,
                         secrets: Secrets = None, **kwargs):
    """
    before-control of the method's execution

    Called by the Chaos Toolkit before the activities of the method are
    applied.
    """
    logger.debug("----------------CONFIGURATION AFTER METHOD:  %s" % configuration)


def after_experiment_control(context: Experiment, state: Journal,
                             configuration: Configuration = None,
                             secrets: Secrets = None, **kwargs):
    """
    after-control of the experiment's execution

    Called by the Chaos Toolkit after the experiment's completed. It passes the
    journal of the execution. At that stage, the after control has no influence
    over the execution however. Please see
    https://docs.chaostoolkit.org/reference/api/journal/#journal-elements
    for more information about the journal.
    """
    date_utils = DateUtils(Timezone.UTC.value)
    logger.debug("AFTER EXPERIMENT CONTROL: %s" % state)
    hadoop_rest_client_utils = HadoopRestClientUtils()
    if hadoop_rest_client_utils.is_yarn_job_finished(APPLICATION_ID):
        job_stats = hadoop_rest_client_utils.get_yarn_job_details(APPLICATION_ID)
        logger.info("Total execution time for yarn job with application id %s: %s ms (i.e %s minutes) " % (
            APPLICATION_ID, job_stats["app"]["elapsedTime"],
            date_utils.get_minutes_from_milliseconds(job_stats["app"]["elapsedTime"])))
    else:
        logger.info("Yarn job with application id %s is not in FINISHED state. Please check." % APPLICATION_ID)
    logger.info("Stats for application id %s: %s" % (
        APPLICATION_ID, hadoop_rest_client_utils.get_yarn_job_details(APPLICATION_ID)))

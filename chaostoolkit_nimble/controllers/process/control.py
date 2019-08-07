from time import sleep

from chaoslib.types import Configuration, \
    Experiment, Run, Secrets, Activity
from chaostoolkit_nimble.controllers.base import control
from logzero import logger

control.configure_control()


# EXPERIMENT_STATUS = None


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
    sleep(3)


def after_method_control(context: Experiment,
                         configuration: Configuration = None,
                         secrets: Secrets = None, **kwargs):
    """
    before-control of the method's execution

    Called by the Chaos Toolkit before the activities of the method are
    applied.
    """
    logger.debug("----------------CONFIGURATION AFTER METHOD:  %s" % configuration)
    sleep(120)

# def after_experiment_control(context: Experiment, state: Journal,
#                              configuration: Configuration = None,
#                              secrets: Secrets = None, **kwargs):
#     """
#     after-control of the experiment's execution
#
#     Called by the Chaos Toolkit after the experiment's completed. It passes the
#     journal of the execution. At that stage, the after control has no influence
#     over the execution however. Please see
#     https://docs.chaostoolkit.org/reference/api/journal/#journal-elements
#     for more information about the journal.
#     """
#     logger.debug("Experiment State----------: %s" % state)
#     logger.debug("Experiment context--------------------: %s" % context)
#     global EXPERIMENT_STATUS
#     EXPERIMENT_STATUS = state["status"]
#     logger.debug("EXPERIMENT_STATUS %s" % EXPERIMENT_STATUS)
#     assert state["status"] == "completed"

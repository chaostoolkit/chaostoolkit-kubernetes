from time import sleep

from chaoslib.types import Configuration, \
    Experiment, Run, Secrets, Activity
from chaostoolkit_nimble.controllers.base import control
from logzero import logger

control.configure_control()

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
    sleep(15)


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

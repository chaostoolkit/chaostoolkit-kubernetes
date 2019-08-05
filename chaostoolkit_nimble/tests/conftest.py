# Do not change the name of the file, since pytest detects it with this name only.

import logging.config
import os

import pytest
from nimble.core import global_constants
from nimble.core.utils.shell_utils import ShellUtils

try:
    os.makedirs(global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH)
except Exception:
    pass

logging.config.fileConfig(global_constants.DEFAULT_LOGGING_FILE_PATH)

# pylint: disable=wrong-import-position
from nimble.core.configs.validation_config_parser import ValidationConfigParser
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.report_utils import ReportUtils
from nimble.actions.base.flows.user_actions import UserActions

OPTIONS_DICT = {}
PREVIOUS_FAILED = None
ITEM_LIST = []


def pytest_addoption(parser):
    parser.addoption("--testbed",
                     help="Relative path (to the project root) of the testbed file. E.g. python -m pytest --testbed=resources/testbeds/open_nebula_134_192.yml")
    parser.addoption("--componentAttributesConfig",
                     help="Relative path (to the project root) of the file containing component attributes configs. E.g. python -m pytest --componentAttributesConfig=resources/components/component_attributes_ambari.yml")
    parser.addoption("--validationConfig",
                     help="Relative path (to the project root) of the file containing validation configs. E.g. python -m pytest --validationConfig=resources/validation/sample_validation_config.yml")
    parser.addoption("--experimentsPath",
                     help="Relative path (to the project root) of the file containing chaos experiment json files. E.g. python -m pytest --validationConfig=resources/validation/chaos_exp_config.yml")


@pytest.fixture(scope="session", autouse=True)
def initialize_node_obj(request):
    testbed_file = request.config.getoption("--testbed")
    component_arttributes_file = request.config.getoption("--componentAttributesConfig")
    if not component_arttributes_file:
        component_arttributes_file = "nimble/resources/components/component_attributes.yml"
    setup_files_base_path = "%s/setup" % global_constants.DEFAULT_LOCAL_TMP_PATH
    if testbed_file:
        NodeManager.initialize(testbed_file, component_arttributes_file)
        ShellUtils.execute_shell_command(
            ShellUtils.remove_and_create_directory(setup_files_base_path))
        testbed_file_tmp_path = "%s/%s" % (setup_files_base_path, testbed_file.rsplit("/", 1)[1])
        component_arttributes_file_tmp_path = "%s/%s" % (
            setup_files_base_path, component_arttributes_file.rsplit("/", 1)[1])
        ShellUtils.execute_shell_command(ShellUtils.copy(testbed_file, testbed_file_tmp_path))
        ShellUtils.execute_shell_command(
            ShellUtils.copy(component_arttributes_file, component_arttributes_file_tmp_path))
    yield
    ShellUtils.execute_shell_command(ShellUtils.remove(setup_files_base_path, recursive=True))


@pytest.fixture(scope="session", autouse=True)
def initialize_arguments(request):
    global OPTIONS_DICT

    for option, value in list(request.config.option.__dict__.items()):
        OPTIONS_DICT[option] = value


@pytest.fixture(scope="session")
def config_parser(initialize_arguments):  # pylint: disable=redefined-outer-name,unused-argument
    """Initialize the validation config parser.

    :param initialize_arguments: Fixture defined above.
    :return: Return the object of the Validation config parser.
    :rtype: :class:`nimble.core.configs.validation_config_parser.ValidationConfigParser`
    """
    return ValidationConfigParser(OPTIONS_DICT["validationConfig"])


@pytest.fixture(scope="session")
def dump_allure_env_file(config_parser, initialize_node_obj):  # pylint: disable=redefined-outer-name,unused-argument
    """Dump the basic environment variables for Allure.

    :param config_parser: Fixture defined above.
    :param initialize_node_obj: Fixture defined above.
    """
    report_dict = ReportUtils.get_generic_attributes(config_parser)
    ReportUtils.dump_allure_env_file(report_dict)


@pytest.fixture(scope="session")
def user_actions(config_parser, dump_allure_env_file):  # pylint: disable=redefined-outer-name,unused-argument
    """Initialize the object for user actions.

    :param config_parser: Fixture defined above.
    :param dump_allure_env_file: Fixture defined above.
    :rtype: :class:`nimble.actions.base.flows.user_actions.UserActions`
    """
    return UserActions(config_parser)


def pytest_runtest_makereport(item, call):
    """
    Sometimes you may have a testing situation which consists of a series of test steps.  If one step fails it makes no
    sense to execute further steps as they are all expected to fail anyway and their tracebacks add no insight.
    This and the next hook implementations work together to abort incremental-marked tests in a class.


    :param item: Pytest's internal fixture.
    :param call: Pytest's internal fixture.
    """
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item  # pylint: disable=protected-access


def pytest_runtest_setup(item):
    """
    Sometimes you may have a testing situation which consists of a series of test steps.  If one step fails it makes no
    sense to execute further steps as they are all expected to fail anyway and their tracebacks add no insight.
    This and the next hook implementations work together to abort incremental-marked tests in a class.

    :param item: Pytest's internal fixture.
    """
    global PREVIOUS_FAILED, ITEM_LIST
    if "incremental" in item.keywords:
        for previous_item in ITEM_LIST:
            if PREVIOUS_FAILED is None:
                PREVIOUS_FAILED = getattr(previous_item.parent, "_previousfailed", None)
            if PREVIOUS_FAILED is not None:
                pytest.fail("previous test failed (%s)" % PREVIOUS_FAILED.name)
        try:
            ITEM_LIST.pop(0)
        except IndexError:
            pass
        ITEM_LIST.append(item)

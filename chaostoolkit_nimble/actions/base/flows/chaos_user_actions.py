import logging

import allure
import jinja2
from nimble.core import global_constants
from nimble.core.utils.shell_utils import ShellUtils
from nimble.tests.conftest import OPTIONS_DICT

_LOGGER = logging.getLogger(__name__)

EXPERIMENTS_BASE_PATH = "%s/tmp/experiments/" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH


def run_experiment(exp_template_file=None, context=None):
    if not exp_template_file:
        experiments_path = OPTIONS_DICT["experimentsPath"]
        ShellUtils.execute_shell_command(ShellUtils.copy(experiments_path, EXPERIMENTS_BASE_PATH))
    else:
        render_template(exp_template_file, context)
    experiment_file_response = ShellUtils.execute_shell_command(
        ShellUtils.find_files_in_directory(EXPERIMENTS_BASE_PATH))
    for experiment_file in experiment_file_response.stdout.strip().split("\n"):
        ShellUtils.execute_shell_command("chaos run %s" % experiment_file)
    html_report_path = generate_html()
    allure.attach.file(html_report_path, name='Chaos experiment html report',
                       attachment_type=allure.attachment_type.HTML)


def render_template(exp_template_file, context):
    ShellUtils.execute_shell_command(ShellUtils.remove_and_create_directory(EXPERIMENTS_BASE_PATH))
    template_base_dir = "chaostoolkit_nimble/resources/exp_templates"
    templateLoader = jinja2.FileSystemLoader(searchpath=template_base_dir)
    # templateLoader = jinja2.FileSystemLoader(searchpath="chaostoolkit_nimble/resources/exp_templates/process")
    templateEnv = jinja2.Environment(loader=templateLoader)
    # exp_template_file = "exp.json"
    template = templateEnv.get_template(exp_template_file)
    _LOGGER.info('Rendering from template: %s' % template.name)
    template.stream(context).dump('%s/exp.json' % EXPERIMENTS_BASE_PATH)


def generate_html():
    journal_json_path = "journal.json"
    html_report_path = "%s/chaos_report.html" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
    command = "export LC_ALL=en_US.UTF-8 && chaos report --export-format=html5 %s %s" % (
        journal_json_path, html_report_path)
    guavus_reposnse = ShellUtils.execute_shell_command(command)
    return html_report_path


def validate(user_actions, callable_, job_alias, transfer_to_file_server=False, validation_entities=None,
             dataset_alias=global_constants.DEFAULT_DATASET_ALIAS, ibs=None, mode=None, output_alias=None, **kwargs):
    user_actions.validate(callable_, job_alias, transfer_to_file_server=transfer_to_file_server,
                          validation_entities=validation_entities,
                          dataset_alias=dataset_alias, ibs=ibs, mode=mode, output_alias=output_alias, **kwargs)
import logging
import re

import allure
import jinja2
from nimble.core import global_constants
from nimble.core.utils.shell_utils import ShellUtils

_LOGGER = logging.getLogger(__name__)

EXPERIMENTS_BASE_PATH = "%s/tmp/experiments/" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
ShellUtils.execute_shell_command(ShellUtils.remove_and_create_directory(EXPERIMENTS_BASE_PATH))


def run_experiment(exp_file=None, exp_template_file=None, context=None):
    status = None
    if exp_file:
        ShellUtils.execute_shell_command(ShellUtils.copy(exp_file, EXPERIMENTS_BASE_PATH))
    else:
        render_template(exp_template_file, context)
    experiment_file_response = ShellUtils.execute_shell_command(
        ShellUtils.find_files_in_directory(EXPERIMENTS_BASE_PATH))
    for experiment_file in experiment_file_response.stdout.strip().split("\n"):
        response = ShellUtils.execute_shell_command("chaos run %s" % experiment_file)
        status = re.search(r'.*Experiment\sended\swith\sstatus:\s(.*)', response.stderr).group(1)
    html_report_path = generate_html()
    allure.attach.file(html_report_path, name='Chaos experiment html report',
                       attachment_type=allure.attachment_type.HTML)
    assert status == "completed"


def render_template(exp_template_file, context):
    template_base_dir = "chaostoolkit_nimble/resources/exp_templates"
    templateLoader = jinja2.FileSystemLoader(searchpath=template_base_dir)
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(exp_template_file)
    _LOGGER.info('Rendering from template: %s' % template.name)
    template.stream(context).dump('%s/exp.json' % EXPERIMENTS_BASE_PATH)


def generate_html():
    journal_json_path = "journal.json"
    html_report_path = "%s/chaos_report.html" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
    command = "export LC_ALL=en_US.UTF-8 && chaos report --export-format=html5 %s %s" % (
        journal_json_path, html_report_path)
    ShellUtils.execute_shell_command(command)
    return html_report_path

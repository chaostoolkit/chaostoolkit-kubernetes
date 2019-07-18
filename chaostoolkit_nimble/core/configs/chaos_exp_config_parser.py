import logging
import os

from nimble.core import global_constants
from nimble.core.adapters.sqlite.sqlite_adapter import SqliteAdapter
from nimble.core.configs.base_yaml_parser import BaseYamlParser
from nimble.core.configs.scheduler_config_factory import SchedulerConfigFactory
from nimble.core.configs.source_config_factory import SourceConfigFactory
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.string_utils import StringUtils


class ChaosExpConfigParser(BaseYamlParser):
    """Methods to fetch the validation attributes from the validation YAML config."""

    def __init__(self, config_path, node_obj=NodeManager.node_obj):
        """

        :param config_path: Path of the config file to be used.
        :type config_path: str
        :type node_obj: :class:`nimble.core.entity.nodes.Nodes`
        """
        self._logger = logging.getLogger(__name__)
        super(ChaosExpConfigParser, self).__init__()
        self.config_path = config_path
        # self.config_obj = self.load_configs(config_path)
        # self.project = self.get_defaults_from_config()["project"]
        # self.build = self.get_defaults_from_config()["build"]
        # self.customer = self.get_defaults_from_config()["customer"]
        # self.stop_jobs_flag = self.get_defaults_from_config().get("stop_jobs", True)
        # self.golden_build = self.get_attribute_or_default_or_pass(self.get_defaults_from_config(), "golden_build")
        # self.mail_to = self.get_defaults_from_config()["mail_to"]
        # self.output_file_name = "output.txt"
        # self.ib_tmp_file = "ib_tmp_file.txt"
        # self.input_tmp_file = "input_tmp_file.txt"
        # self.project = self.get_defaults_from_config()["project"]
        # self.build = self.get_defaults_from_config()["build"]
        # self.customer = self.get_defaults_from_config()["customer"]
        # self.base_http_path = "modules/%s/%s/%s" % (self.project, self.golden_build, self.customer)
        # self.base_latest_http_path = "modules/%s/%s_latest/%s" % (self.project, self.build, self.customer)
        # self.separator = ','
        # self.sqlite_file_path = "%s/validation_entities.db" % global_constants.DEFAULT_LOCAL_ARTIFACTS_PATH
        # self.urlcat_delimiter = "^^"
        # self.sqlite_adapter = SqliteAdapter(db_file=self.sqlite_file_path)
        # node_obj.fetch_timestamp_from_server()

    # def get_job_schedule_configs(self, job_alias):
    #     return SchedulerConfigFactory.get(self.get_job_schedule_source(job_alias), self.config_obj).get_configs(
    #         self.get_job_schedule(job_alias))
    #
    # def get_ibs(self):
    #     return self.get_attribute_or_default_or_pass(self.config_obj, "ibs")
    #
    # def get_ib_attributes(self, ib_alias):
    #     return self.get_attribute_or_pass(self.get_ibs(), ib_alias)
    #
    # def get_ib_source(self, ib_alias):
    #     return self.get_attribute_or_default_or_pass(self.get_ib_attributes(ib_alias), "source")
    #
    # def get_ib_source_configs(self, ib_alias):
    #     return SourceConfigFactory.get(self.get_ib_source(ib_alias), self.config_obj).get_configs(
    #         self.get_ib_attributes(ib_alias))
    #
    # def get_input_source_configs(self, job_alias, input_alias):
    #     """Get the attributes for input source for a given job and input alias from the YAML config file.
    #
    #     :param job_alias: Job alias for which the input source attributes are to be fetched.
    #     :type job_alias: str
    #     :param input_alias: Input alias for which the source attributes are to be fetched.
    #     :type input_alias: str
    #     :return: Ordered dictionary of input source attributes.
    #     :rtype: :class:`collections.OrderedDict`
    #     """
    #     return SourceConfigFactory.get(self.get_input_source(job_alias, input_alias), self.config_obj).get_configs(
    #         self.get_input_attributes(job_alias, input_alias))
    #
    # def get_job_actual_output_source_configs(self, job_alias, output_alias):
    #     """Get the attributes for actual output source for a given job and input alias from the YAML config file.
    #
    #     :param job_alias: Job alias for which the actual output source attributes are to be fetched.
    #     :type job_alias: str
    #     :param output_alias: Output alias for which the actual output source attributes are to be fetched.
    #     :type output_alias: str
    #     :return: Ordered dictionary of actual output source attributes.
    #     :rtype: :class:`collections.OrderedDict`
    #     """
    #     source = self.get_job_actual_output_source(job_alias, output_alias)
    #     return SourceConfigFactory.get(source, self.config_obj).get_configs(
    #         self.get_job_actual_output_attributes(job_alias, output_alias))
    #
    # def get_urlcat_command_attributes(self, job_alias, input_alias):
    #     """Get the urlcat command attributes for the given job and input alias from the YAML config file.
    #
    #     :param job_alias: Job alias for which the urlcat command attributes are to be fetched.
    #     :type job_alias: str
    #     :param input_alias: Input alias for which the urlcat command attributes are to be fetched.
    #     :type input_alias: str
    #     :return: Ordered dictionary of `urlcat_command` attributes.
    #     :rtype: :class:`collections.OrderedDict`
    #     """
    #     return self.get_attribute_or_default_or_pass(self.get_input_attributes(job_alias, input_alias),
    #                                                  "urlcat_command")
    #
    # def get_urlcat_command_input_select_query(self, job_alias, input_alias):
    #     """Get the input select query for the given job and input alias from the YAML config file.
    #
    #     This is the query given to fetch data from sqlite which will form the input for URLCat input. The URLcat command
    #     will operate on the fields selected through this query and generate an output accordingly.
    #
    #     :param job_alias: Job alias for which the input select query is to be fetched.
    #     :type job_alias: str
    #     :param input_alias: Input alias for which the input select query is to be fetched.
    #     :type input_alias: str
    #     :return: Input select query.
    #     :rtype: str
    #     """
    #     return self.get_attribute_or_default_or_pass(self.get_urlcat_command_attributes(job_alias, input_alias),
    #                                                  "input_select_query")
    #
    # def get_urlcat_regression_ibs(self):
    #     """Get the url paths for all four `iv` and `ibstore` ibs that are supplied as job input parameters on jenkins.
    #
    #     :return: Return all ib's url paths or None for each ib in case ib parameters are not supplied with the job.
    #     :rtype: tuple
    #     """
    #     try:
    #         iv_url_expected = os.environ["iv_url_expected"]
    #         ibstore_url_expected = os.environ["ibstore_url_expected"]
    #         iv_url_actual = os.environ["iv_url_actual"]
    #         ibstore_url_actual = os.environ["ibstore_url_actual"]
    #         return (iv_url_expected, ibstore_url_expected, iv_url_actual,
    #                 ibstore_url_actual)
    #     except KeyError:
    #         return None, None, None, None
    #
    # def get_urlcat_ib_versions(self):
    #     """Get the version number for expected as well as actual ibs.
    #
    #     :return: Return both the version numbers or None for each set of ibs in case ib parameters are not supplied
    #         with the job.
    #     :rtype: tuple
    #     """
    #     try:
    #         ib_version_expected = \
    #             StringUtils.none_safe_string(self.get_urlcat_regression_ibs()[0]).replace("//", "/").split("/")[4]
    #         ib_version_actual = \
    #             StringUtils.none_safe_string(self.get_urlcat_regression_ibs()[2]).replace("//", "/").split("/")[4]
    #         return (ib_version_expected, ib_version_actual)
    #     except IndexError:
    #         return None, None

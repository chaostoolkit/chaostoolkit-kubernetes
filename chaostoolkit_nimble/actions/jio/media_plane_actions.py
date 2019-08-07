import collections
import logging
import re

import mmh3
from chaostoolkit_nimble.actions.jio.common_actions import CommonActions
from nimble.actions.base.regression.config_actions import ConfigActions
from nimble.core.entity.components import Components
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.shell_utils import ShellUtils


class MediaPlaneActions(object):

    def __init__(self, job_alias, config_parser, job_user="ambari-qa"):

        self._logger = logging.getLogger(__name__)
        self.job_alias = job_alias
        self.comman_action = CommonActions()
        self.seed = 42
        self.date_format_all = '%Y%m%d%H%M%S'
        self.date_format_usual = "%Y-%m-%d %H:%M:%S"
        self.frequency = 900
        self.config_actions = ConfigActions()
        self.job_user = job_user
        actual_output_configs = config_parser.get_job_actual_output_source_configs(self.job_alias, "output1")
        self.database_name = actual_output_configs["db_name"]
        self.table_name = actual_output_configs["table_name"]
        self.node_alias = NodeManager.node_obj.get_node_aliases_by_component(Components.MANAGEMENT.name)[0]

    def schedule_15_min_job(self):
        job_base_directory = "/data/jio_copy/microapp1/"
        job_config_file = "%s/conf/MediaPlaneJob.json" % job_base_directory
        job_script_file = "%s/scripts/media_plane_microapp1.sh" % job_base_directory

        ######## Update job config file
        kwargs = collections.OrderedDict()
        kwargs["config_separator"] = "="
        kwargs["location"] = "local"
        kwargs["base_path"] = job_config_file
        kwargs["file_format"] = "json"
        kwargs["components"] = [Components.MANAGEMENT.name]
        kwargs["properties"] = {"mediaPlaneRawInput.type": "csv", "mediaPlaneRawInput.header": "true",
                                "mediaPlaneRawInput.pathPrefix": "/tmp/partition_date=",
                                "mediaPlaneProcessedOutput.tableName": "%s.%s" % (self.database_name, self.table_name)}
        self.config_actions.update_configs(**kwargs)

        ######## Update job script file
        NodeManager.node_obj.execute_command_on_node(self.node_alias,
                                                     ShellUtils.find_and_replace_whole_line_in_file("basedirectory=",
                                                                                                    "basedirectory=/data/jio_copy/microapp1/",
                                                                                                    job_script_file))
        NodeManager.node_obj.execute_command_on_node(self.node_alias,
                                                     ShellUtils.find_and_replace_whole_line_in_file("lastdayepoch=",
                                                                                                    """lastdayepoch=`date -d "2019-07-20 05:30:00" +%s`""",
                                                                                                    job_script_file))
        NodeManager.node_obj.execute_command_on_node(self.node_alias, ShellUtils.find_and_replace_in_file(
            "--timeIncrementInFilesInMin=15", "--timeIncrementInFilesInMin=15", job_script_file))
        NodeManager.node_obj.execute_command_on_node(self.node_alias, ShellUtils.find_and_replace_in_file(
            "--durationOfDataToProcessInMin=15", "--durationOfDataToProcessInMin=15", job_script_file))
        ############# Run job on management node
        job_run_command = "export SPARK_HOME=/usr/hdp/2.6.5.0-292/spark2 && cd %s && nohup scripts/media_plane_microapp1.sh >> a.out 2>>a.out &" % (
            job_base_directory)
        NodeManager.node_obj.execute_remote_command_in_bg(self.node_alias, job_run_command)

    def none_or_value(self, value):
        if str(value) == "":
            return None
        else:
            return value

    def generate_cell_id(self, mcc, mnc, cell_id):
        if mcc == '' or mnc == '' or cell_id == '':
            return '-1'
        else:
            if str(mnc) != 3:
                final_mnc = '0' * (3 - len(str(mnc))) + str(mnc)
            else:
                final_mnc = mnc

        return str(mcc) + str(final_mnc) + '0' * (9 - len(str(cell_id))) + str(cell_id)

    def generate_hash(self, source_ip, source_port, dest_ip, dest_port):
        hash_input_string = "%s|%s|%s|%s" % (source_ip, source_port, dest_ip, dest_port)
        hash_value = mmh3.hash(hash_input_string, self.seed)
        return hash_value

    def generate_binary_error_code(self, list_of_flags):
        binary_string = "".join(list_of_flags)
        binary_code = int(binary_string, 2)
        return binary_code

    def link_specific_list(self, list):
        default_list = [None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        if len(list) == 0:
            return default_list
        else:
            if self.none_or_value(list[34]).startswith("2405:0203") or self.none_or_value(list[34]).startswith(
                    "2405:0204") or self.none_or_value(list[34]).startswith("2405:0205") or self.none_or_value(
                list[34]).startswith("2409:4000"):
                return [self.none_or_value(list[34]), self.none_or_value(list[35]), self.none_or_value(list[19]),
                        self.none_or_value(list[20]), self.none_or_value(list[45]), self.none_or_value(list[43]),
                        self.none_or_value(list[11]), self.none_or_value(list[12]), self.none_or_value(list[22]),
                        self.none_or_value(list[26]), self.none_or_value(list[27]), self.none_or_value(list[32]),
                        self.none_or_value(list[33]), self.none_or_value(list[36])]
            # m_u_source_ip , m_u_source_port , m_u_destination_ip , m_u_destination_port , subscriber_id , subscriber_msisdn , media_active_time_seconds , media_completed_indicator , media_long_call_indicator , media_middle_gap_indicator , media_short_call_indicator , media_single_direction_indicator , media_start_gap_indicator
            # checked if its uplink record

            else:
                return [self.none_or_value(list[19]), self.none_or_value(list[20]), self.none_or_value(list[34]),
                        self.none_or_value(list[35]), self.none_or_value(list[45]), self.none_or_value(list[43]),
                        self.none_or_value(list[11]), self.none_or_value(list[12]), self.none_or_value(list[22]),
                        self.none_or_value(list[26]), self.none_or_value(list[27]), self.none_or_value(list[32]),
                        self.none_or_value(list[33]), self.none_or_value(list[36])]
            # m_u_destination_ip , m_u_destination_port , m_u_source_ip , m_u_source_port, subscriber_id , subscriber_msisdn , media_active_time_seconds , media_completed_indicator , media_long_call_indicator , media_middle_gap_indicator , media_short_call_indicator , media_single_direction_indicator , media_start_gap_indicator
            # checked if its down_link record

    def validate_media_plane(self, validation_entities):
        hashed_row_dict = {}
        min_time = \
            validation_entities.sqlite_adapter.select("select min(cal_timestamp_time) from %s_input1" % self.job_alias)[
                -1][
                0]

        max_time = \
            validation_entities.sqlite_adapter.select("select max(cal_timestamp_time) from %s_input1" % self.job_alias)[
                -1][
                0]

        time_range_list = self.comman_action.get_time_range_list(min_time, max_time, self.frequency,
                                                                 date_time_format=self.date_format_usual)
        media_header = ['m_hash_tuple', 'm_timestamp', 'm_u_source_ip', 'm_u_source_port', 'm_u_destination_ip',
                        'm_u_destination_port', 'm_u_imsi', 'm_u_msisdn', 'm_u_call_duration', 'm_u_call_completed',
                        'm_u_end_gap_indicator', 'm_u_long_call_indicator', 'm_u_middle_gap_indicator',
                        'm_u_short_call_indicator', 'm_u_one_way_audio', 'm_u_start_gap_indicator',
                        'm_u_weighted_jitter_total', 'm_u_weighted_mos_total', 'm_u_weighted_packet_loss_total',
                        'm_u_weighted_rtd_total', 'm_u_jitter_sum', 'm_u_rtd_sum', 'm_u_packet_loss_sum',
                        'm_u_degradation_sum', 'm_u_cell_id', 'm_d_destination_ip', 'm_d_destination_port',
                        'm_d_source_ip', 'm_d_source_port', 'm_d_imsi', 'm_d_msisdn', 'm_d_call_duration',
                        'm_d_call_completed', 'm_d_end_gap_indicator', 'm_d_long_call_indicator',
                        'm_d_middle_gap_indicator', 'm_d_short_call_indicator', 'm_d_one_way_audio',
                        'm_d_start_gap_indicator', 'm_d_weighted_jitter_total', 'm_d_weighted_mos_total',
                        'm_d_weighted_packet_loss_total', 'm_d_weighted_rtd_total', 'm_d_jitter_sum', 'm_d_rtd_sum',
                        'm_d_packet_loss_sum', 'm_d_degradation_sum', 'm_d_cell_id', 'm_error_code', 'm_ue_ip',
                        'm_msisdn', 'm_imsi', 'm_cell_id', 'm_call_id', 'm_weighted_mos_sum', 'm_weighted_jitter_sum',
                        'm_weighted_packet_loss_sum', 'm_weighted_rtd_sum', 'm_degradation_sum', 'm_jitter_sum',
                        'm_packet_loss_sum', 'm_rtd_sum', 'm_mos', 'm_jitter', 'm_packet_loss', 'm_rtd',
                        'm_binned_timestamp', 'sql_timestamp']
        final_media_dump = [media_header]
        time_columns = self.comman_action.get_time_colums(frequency=self.frequency)
        final_media_dump[0].extend(time_columns.split(','))
        for time_range in time_range_list:
            where_clause = "cal_timestamp_time >= '%s' and cal_timestamp_time < '%s'" % (time_range[0], time_range[1])
            total_dump = validation_entities.sqlite_adapter.select(
                "select * from %s_input1 where %s" % (self.job_alias, where_clause))
            temp_list = []
            hashed_row_dict = {}
            for row in total_dump[1:]:
                temp_dict = {}
                row = list(row)
                if row[19].startswith("2405:0203") or row[19].startswith("2405:0204") or row[19].startswith(
                        "2405:0205") or row[19].startswith("2409:4000"):
                    hash_value = self.generate_hash(row[19], row[20], row[34], row[35])
                elif row[34].startswith("2405:0203") or row[34].startswith("2405:0204") or row[34].startswith(
                        "2405:0205") or row[34].startswith("2409:4000"):
                    hash_value = self.generate_hash(row[34], row[35], row[19], row[20])
                else:
                    continue
                if hash_value in hashed_row_dict.keys():
                    if row[19].startswith("2405:0203") or row[19].startswith("2405:0204") or row[19].startswith(
                            "2405:0205") or row[19].startswith("2409:4000"):
                        hashed_row_dict[hash_value]["downlink"] = row
                    elif row[34].startswith("2405:0203") or row[34].startswith("2405:0204") or row[34].startswith(
                            "2405:0205") or row[34].startswith("2409:4000"):
                        hashed_row_dict[hash_value]["uplink"] = row
                    else:
                        continue
                else:
                    if row[19].startswith("2405:0203") or row[19].startswith("2405:0204") or row[19].startswith(
                            "2405:0205") or row[19].startswith("2409:4000"):
                        temp_dict = {"downlink": row, "uplink": []}
                    elif row[34].startswith("2405:0203") or row[34].startswith("2405:0204") or row[34].startswith(
                            "2405:0205") or row[34].startswith("2409:4000"):
                        temp_dict = {"downlink": [], "uplink": row}
                    else:
                        continue
                    hashed_row_dict[hash_value] = temp_dict

            for hash_value in hashed_row_dict.keys():
                error_code_list = ['1', '1']
                media_uplink_row = hashed_row_dict[hash_value]["uplink"]
                media_downlink_row = hashed_row_dict[hash_value]["downlink"]
                media_u_row = self.link_specific_list(media_uplink_row)
                media_d_row = self.link_specific_list(media_downlink_row)
                if len(media_uplink_row) == 0:
                    m_timestamp = (re.sub('[^A-Za-z0-9]+', "", media_downlink_row[1]))
                    m_binned_timestamp = (
                        re.sub('[^A-Za-z0-9]+', "", self.comman_action.computeBinTime(media_downlink_row[1])))
                    sql_timestamp = self.comman_action.date_format_changer(m_binned_timestamp, "%Y%m%d%H%M%S",
                                                                           "%Y-%m-%d %H:%M:%S")
                    m_ueip = media_downlink_row[19]
                    m_msisdn = media_uplink_row[43]
                    m_imsi = media_uplink_row[45]
                    error_code_list[0] = 0
                    m_u_wei_mos = 0
                    m_u_wei_jitter = 0
                    m_u_wei_pakt_los = 0
                    m_u_wei_rtd = 0
                    m_u_degradation_sum = 0
                    m_u_jitter_sum = 0
                    m_u_pakt_los_sum = 0
                    m_u_rtd_sum = 0
                    m_u_cell_id = -1
                    m_u_calculated_item = [str(m_u_wei_jitter), str(m_u_wei_mos), str(m_u_wei_pakt_los),
                                           str(m_u_wei_rtd), str(m_u_jitter_sum), str(m_u_rtd_sum),
                                           str(m_u_pakt_los_sum), str(m_u_degradation_sum), str(m_u_cell_id)]
                    m_cell_id = m_u_cell_id

                else:
                    m_timestamp = (re.sub('[^A-Za-z0-9]+', "", media_uplink_row[1]))
                    m_binned_timestamp = (
                        re.sub('[^A-Za-z0-9]+', "", self.comman_action.computeBinTime(media_uplink_row[1])))
                    sql_timestamp = self.comman_action.date_format_changer(m_binned_timestamp, "%Y%m%d%H%M%S",
                                                                           "%Y-%m-%d %H:%M:%S")
                    m_ueip = media_uplink_row[34]
                    m_msisdn = media_uplink_row[43]
                    m_imsi = media_uplink_row[45]
                    m_u_wei_mos = int(media_uplink_row[38])
                    m_u_wei_jitter = int(media_uplink_row[37])
                    m_u_wei_pakt_los = int(media_uplink_row[39])
                    m_u_wei_rtd = int(media_uplink_row[40])
                    m_u_degradation_sum = int(media_uplink_row[13]) + int(media_uplink_row[14]) + int(
                        media_uplink_row[15])
                    m_u_jitter_sum = int(media_uplink_row[23]) + int(media_uplink_row[24]) + int(media_uplink_row[25])
                    m_u_pakt_los_sum = str(
                        int(media_uplink_row[28]) + int(media_uplink_row[29]) + int(media_uplink_row[30]))
                    m_u_rtd_sum = int(media_uplink_row[16]) + int(media_uplink_row[17]) + int(media_uplink_row[18])
                    m_u_cell_id = self.generate_cell_id(media_uplink_row[6], media_uplink_row[7], media_uplink_row[3])
                    m_u_calculated_item = [str(m_u_wei_jitter), str(m_u_wei_mos), str(m_u_wei_pakt_los),
                                           str(m_u_wei_rtd), str(m_u_jitter_sum), str(m_u_rtd_sum),
                                           str(m_u_pakt_los_sum), str(m_u_degradation_sum), str(m_u_cell_id)]
                    m_cell_id = m_u_cell_id

                if len(media_downlink_row) == 0:
                    m_timestamp = (re.sub('[^A-Za-z0-9]+', "", media_uplink_row[1]))
                    m_binned_timestamp = (
                        re.sub('[^A-Za-z0-9]+', "", self.comman_action.computeBinTime(media_uplink_row[1])))
                    sql_timestamp = self.comman_action.date_format_changer(m_binned_timestamp, "%Y%m%d%H%M%S",
                                                                           "%Y-%m-%d %H:%M:%S")
                    m_ueip = media_uplink_row[34]
                    m_msisdn = media_downlink_row[43]
                    m_imsi = media_downlink_row[45]
                    error_code_list[1] = 0
                    m_d_wei_mos = 0
                    m_d_wei_jitter = 0
                    m_d_wei_pakt_los = 0
                    m_d_wei_rtd = 0
                    m_d_degradation_sum = 0
                    m_d_jitter_sum = 0
                    m_d_pakt_los_sum = 0
                    m_d_rtd_sum = 0
                    m_d_cell_id = -1
                    m_d_calculated_item = [str(m_d_wei_jitter), str(m_d_wei_mos), str(m_d_wei_pakt_los),
                                           str(m_d_wei_rtd), str(m_d_jitter_sum), str(m_d_rtd_sum),
                                           str(m_d_pakt_los_sum), str(m_d_degradation_sum), str(m_d_cell_id)]
                    m_cell_id = m_d_cell_id

                else:
                    m_timestamp = (re.sub('[^A-Za-z0-9]+', "", media_downlink_row[1]))
                    m_binned_timestamp = (
                        re.sub('[^A-Za-z0-9]+', "", self.comman_action.computeBinTime(media_downlink_row[1])))
                    sql_timestamp = self.comman_action.date_format_changer(m_binned_timestamp, "%Y%m%d%H%M%S",
                                                                           "%Y-%m-%d %H:%M:%S")
                    m_ueip = media_downlink_row[19]
                    m_msisdn = media_downlink_row[43]
                    m_imsi = media_downlink_row[45]
                    m_d_wei_mos = int(media_downlink_row[38])
                    m_d_wei_jitter = int(media_downlink_row[37])
                    m_d_wei_pakt_los = int(media_downlink_row[39])
                    m_d_wei_rtd = int(media_downlink_row[40])
                    m_d_degradation_sum = int(media_downlink_row[13]) + int(media_downlink_row[14]) + int(
                        media_downlink_row[15])
                    m_d_jitter_sum = int(media_downlink_row[23]) + int(media_downlink_row[24]) + int(
                        media_downlink_row[25])
                    m_d_pakt_los_sum = int(media_downlink_row[28]) + int(media_downlink_row[29]) + int(
                        media_downlink_row[30])
                    m_d_rtd_sum = int(media_downlink_row[16]) + int(media_downlink_row[17]) + int(
                        media_downlink_row[18])
                    m_d_cell_id = self.generate_cell_id(media_downlink_row[6], media_downlink_row[7],
                                                        media_downlink_row[3])
                    m_d_calculated_item = [str(m_d_wei_jitter), str(m_d_wei_mos), str(m_d_wei_pakt_los),
                                           str(m_d_wei_rtd), str(m_d_jitter_sum), str(m_d_rtd_sum),
                                           str(m_d_pakt_los_sum), str(m_d_degradation_sum), str(m_d_cell_id)]
                    m_cell_id = m_d_cell_id

                m_hash_tuple = hash_value
                m_error_code = self.generate_binary_error_code(error_code_list)
                m_call_id = "m_" + str(m_ueip) + "_" + str(m_hash_tuple)
                m_wei_mos = int(m_u_wei_mos) + int(m_d_wei_mos)
                m_wei_jitter = int(m_u_wei_jitter) + int(m_d_wei_jitter)
                m_wei_pkt_los = int(m_u_wei_pakt_los) + int(m_d_wei_pakt_los)
                m_wei_rtd = int(m_u_wei_rtd) + int(m_d_wei_rtd)
                m_degradation_sum = int(m_u_degradation_sum) + int(m_d_degradation_sum)
                m_jitter_sum = int(m_u_jitter_sum) + int(m_d_jitter_sum)
                m_pkt_loss_sum = int(m_u_pakt_los_sum) + int(m_d_pakt_los_sum)
                m_rtd_sum = int(m_u_rtd_sum) + int(m_d_rtd_sum)
                m_mos = float(m_wei_mos) / m_degradation_sum / 100
                m_jitter = float(m_wei_jitter) / m_jitter_sum
                m_packet_loss = float(m_wei_pkt_los) / m_pkt_loss_sum / 100
                m_rtd = float(m_wei_rtd) / m_rtd_sum

                time_array = self.comman_action.time_column_needful(self.frequency, m_binned_timestamp)

                media_output_list = [str(m_hash_tuple), str(
                    m_timestamp)] + media_u_row + m_u_calculated_item + media_d_row + m_d_calculated_item + [
                                        str(m_error_code), str(m_ueip), str(m_msisdn), str(m_imsi), str(m_cell_id),
                                        str(m_call_id), str(m_wei_mos), str(m_wei_jitter), str(m_wei_pkt_los),
                                        str(m_wei_rtd), str(m_degradation_sum), str(m_jitter_sum), str(m_pkt_loss_sum),
                                        str(m_rtd_sum), str(m_mos), str(m_jitter), str(m_packet_loss), str(m_rtd),
                                        str(m_binned_timestamp), str(sql_timestamp)] + time_array
                temp_list.append(media_output_list)
            final_media_dump.extend(temp_list)
        validation_entities.output_obj[self.job_alias]["output1"] = final_media_dump

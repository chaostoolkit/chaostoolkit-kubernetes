import logging

from nimble.core.entity.components import Components
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.components.hadoop_utils import HadoopUtils
from nimble.core.utils.shell_utils import ShellUtils
from nimble.core.utils.date_utils import DateUtils, Timezone


class CommonActions(object):

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self.hadoop_utils = HadoopUtils
        self.date_utils = DateUtils(Timezone.UTC.value)
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.bin_interval = 900

    def hdfs_keytab(self):
        hadoop_utils = HadoopUtils(NodeManager.node_obj)
        mgt_alias = hadoop_utils.master_namenode
        hdfs_keytab = NodeManager.node_obj.execute_command_on_node(mgt_alias,"klist -tke /etc/security/keytabs/hdfs.headless.keytab |grep '@' |awk -F' ' '{print $4}'|head -1")
        kinit_command = "kinit -kt /etc/security/keytabs/hdfs.headless.keytab %s" % hdfs_keytab.stdout
        NodeManager.node_obj.execute_command_on_component(Components.MASTER_NAMENODE.name,ShellUtils.su("hdfs", kinit_command))

    def computeBinTime(self, timestamp):
        epoch_time = self.date_utils.convert_human_readable_to_epoch(timestamp, self.date_format)
        bin_epoch = self.date_utils.round_down_epoch(epoch_time, self.bin_interval)
        bin_timestamp = self.date_utils.convert_epoch_to_human_readable(bin_epoch, self.date_format)
        return bin_timestamp

    def calc_end_time(self, start_time, duration):
        epoch_start_time = self.date_utils.convert_human_readable_to_epoch(start_time[:-4], self.date_format)
        epoch_end_time = str(format((float(epoch_start_time) + float(duration)), '.6f'))
        end_time = self.date_utils.convert_epoch_to_human_readable(float(epoch_end_time), self.date_format)
        return end_time

    def date_format_changer(self, input_date, input_date_format, output_date_format):
        epoch_input = self.date_utils.convert_human_readable_to_epoch(input_date,input_date_format)
        return self.date_utils.convert_epoch_to_human_readable(epoch_input, output_date_format)

    def get_time_range_list(self, min_time, max_time, frequency, date_time_format):
        tmp_list = []
        time_range_list = []
        min_time_epoch = self.date_utils.convert_human_readable_to_epoch(min_time, date_time_format)
        max_time_epoch = self.date_utils.convert_human_readable_to_epoch(max_time, date_time_format)
        min_round_down = self.date_utils.round_down_epoch(min_time_epoch, frequency)
        max_round_down = self.date_utils.round_up_epoch(max_time_epoch, frequency)
        if min_round_down == max_round_down:
            max_round_up = self.date_utils.round_up_epoch(max_time_epoch, frequency)
            time_range_list = [(self.date_utils.convert_epoch_to_human_readable(min_round_down, date_time_format),
                                self.date_utils.convert_epoch_to_human_readable(max_round_up, date_time_format))]
        else:
            while min_round_down <= max_round_down:
                tmp_list.append(min_round_down)
                min_round_down += frequency
            for index in range(0, (len(tmp_list) - 1)):
                time_range_list.append((
                                       self.date_utils.convert_epoch_to_human_readable(tmp_list[index], date_time_format),
                                       self.date_utils.convert_epoch_to_human_readable(tmp_list[index + 1],
                                                                                       date_time_format)))
        return time_range_list

    def get_time_colums(self, frequency):
        if frequency < 60:
            return "year,month,day,hour,minute,seconds"
        elif frequency >= 60 and frequency < 3600:
            return "year,month,day,hour,minute"
        elif frequency <= 3600 and frequency < 86400:
            return "year,month,day,hour"
        elif frequency <= 86400 and frequency < 2592000:
            return "year,month,day"
        elif frequency <= 2592000 and frequency < 31536000:
            return "year,month"
        elif frequency <= 31536000:
            return "year"
        else:
            self._logger.error("Incorrect Frequency Provided : %s" % frequency)

    def time_column_needful(self, frequency, timestamp_in_ns):
        year = int(timestamp_in_ns[:4])
        month = int(timestamp_in_ns[4:6])
        day = int(timestamp_in_ns[6:8])

        time_columns = self.get_time_colums(frequency)

        if len(time_columns.split(',')) == 3:
            return [year, month, day]
        if len(time_columns.split(',')) == 4:
            hour = int(timestamp_in_ns[8:10])
            return [year, month, day, hour]
        if len(time_columns.split(',')) == 5:
            hour = int(timestamp_in_ns[8:10])
            minute = int(timestamp_in_ns[10:12])
            return [year, month, day, hour, minute]
        if len(time_columns.split(',')) == 6:
            hour = int(timestamp_in_ns[8:10])
            minute = int(timestamp_in_ns[10:12])
            second = int(timestamp_in_ns[12:14])
            return [year, month, day, hour, minute, second]
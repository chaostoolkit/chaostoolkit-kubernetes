from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.components.hadoop_utils import HadoopUtils


def launch_application():
    hadoop_utils = HadoopUtils()
    master_namenode = hadoop_utils.master_namenode
    command = "sleep 5m"
    NodeManager.node_obj.execute_command_on_node(master_namenode, command)
    a = 1

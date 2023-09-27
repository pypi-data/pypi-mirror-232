import os
from happy_python import HappyLog

script_dir = os.path.dirname(os.path.abspath(__file__))
log_conf_file = os.path.join(script_dir, '../conf', 'log.ini')
hlog = HappyLog.get_instance(log_conf_file)

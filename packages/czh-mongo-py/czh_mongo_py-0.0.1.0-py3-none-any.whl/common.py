from happy_python import HappyLog
from pathlib import Path
import os


conf_dir = Path(__file__).parent / 'conf'
log_conf_file = conf_dir / 'log.ini'

hlog = HappyLog.get_instance(str(log_conf_file))
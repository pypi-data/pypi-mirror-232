from datetime import datetime
import logging.config
from pathlib import Path
from string import Template
from typing import Optional, TextIO
import yaml

system_stdout, system_stderr, program_stdout, program_stderr = \
    (logging.getLogger(name) for name in ('system_stdout', 'system_stderr', 'program_stdout', 'program_stderr'))


def configure_logging(level: str, user_config: Optional[TextIO]) -> str:
    log_file_path = f'/tmp/datasphere/job_{datetime.now().isoformat()}.log'
    Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)
    if user_config:
        cfg_str_tpl = user_config.read()
    else:
        cfg_str_tpl = Path(__file__).with_name('logging.yaml').read_text()
    cfg_str = Template(cfg_str_tpl).substitute({'LOG_LEVEL': level, 'LOG_FILE_PATH': log_file_path})
    cfg = yaml.safe_load(cfg_str)
    logging.config.dictConfig(cfg)
    return log_file_path

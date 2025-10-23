import logging.config
import yaml
import os

def setup_logging(
    default_path='logging_config.yml',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
            except Exception as e:
                print(f"Error in Logging Configuration: {e}")
                logging.basicConfig(level=default_level)
    else:
        logging.basicConfig(level=default_level)
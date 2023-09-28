import os

from trail.libconfig import libconfig
from trail.userconfig.config import MainConfig


primary_config_path = os.path.expanduser(libconfig.PRIMARY_USER_CONFIG_PATH)

if os.path.isfile(primary_config_path):
    config_path = primary_config_path
    userconfig = MainConfig(config_path)
else:
    raise Exception("No user config found. Please run `trail init`.")



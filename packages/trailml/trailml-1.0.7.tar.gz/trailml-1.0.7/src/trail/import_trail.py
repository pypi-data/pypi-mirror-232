import os
from trail.libconfig import libconfig

primary_config_path = os.path.expanduser(libconfig.PRIMARY_USER_CONFIG_PATH)


def import_trail():
    if os.path.isfile(primary_config_path):
        from trail.trail import Trail
        return Trail
    else:
        raise Exception("TTTT No config file found. Please run `trail init`")

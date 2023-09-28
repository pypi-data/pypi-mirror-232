import argparse
from .cli_configuration_workflow import login_user


import os

from .libconfig import libconfig
from .userconfig.config import MainConfig


primary_config_path = os.path.expanduser(libconfig.PRIMARY_USER_CONFIG_PATH)

if os.path.isfile(primary_config_path):
    from .trail import Trail


def parse():
    parser = argparse.ArgumentParser(description='Trail Command-Line Tool')
    parser.add_argument(
        '--upload-folder', '-uf',
        required=False,
        help='Upload the specified folder to trail'
    )

    init_parser = parser.add_subparsers(dest='init')
    init_parser.add_parser(
        'init',
        help='Initialize a new trail configuration file'
    )

    args = parser.parse_args()

    if args.upload_folder:
        from .utils import upload_folder
        print(f'Uploading folder: {args.upload_folder}')
        upload_folder(
            local_folder=args.upload_folder,
            expiration_seconds=300
        )

    if args.init:
        print('Initializing new trail configuration file.')
        print('Your configuration will be stored in the current directory. '
              'Make sure that you are in the root directory of your project.')
        username = input('Enter your trail user e-mail: ')
        password = input('Enter your trail password: ')
        login_user(
            useremail=username,
            userpassword=password,
        )


if __name__ == "__main__":
    parse()
    from .trail import Trail


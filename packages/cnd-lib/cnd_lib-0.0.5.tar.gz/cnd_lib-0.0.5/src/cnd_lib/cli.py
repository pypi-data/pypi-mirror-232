import argparse
from .__version__ import (
    __version__,
)
from .cnd_lib import CndLib


def main():
    arguments = _parse_arguments()
    action_done = False
    if arguments.version:
        print(__version__)
        return
    if arguments.module:
        CndLib.new_module(arguments.module)
        action_done = True
    if arguments.lib:
        CndLib.new_lib(arguments.lib)
        action_done = True
    if action_done is False:
        print("You need to indicate what you want. Please use --help to learn how to use it")
        return


def _parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--version',  default=False, action='store_true', help='display the version')
    parser.add_argument('-m', '--module', help='Create new module with test file')
    parser.add_argument('-l', '--lib', help='Create new lib structure')

    return parser.parse_args()
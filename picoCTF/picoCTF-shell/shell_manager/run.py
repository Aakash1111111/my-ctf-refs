#!/usr/bin/env python3
"""
Shell Manager -- Tools for deploying and packaging problems.
"""

import logging
from argparse import ArgumentParser

import coloredlogs
from hacksport.install import (
    install_problems,
    uninstall_problems,
    install_bundle,
    uninstall_bundle,
)
from hacksport.deploy import deploy_problems, undeploy_problems
from hacksport.status import clean, publish, status
from hacksport.containerize import containerize_problems
from shell_manager.config import print_configuration, set_configuration_option
from shell_manager.util import FatalException

coloredlogs.DEFAULT_LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s: %(message)s"
coloredlogs.DEFAULT_DATE_FORMAT = "%H:%M:%S"

logger = logging.getLogger(__name__)


def main():
    parser = ArgumentParser(description="Shell Manager")
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="show debug information",
    )
    parser.add_argument(
        "--colorize",
        default="auto",
        choices=["auto", "never"],
        help="support colored output",
    )
    subparsers = parser.add_subparsers()

    install_parser = subparsers.add_parser("install", help="problem installation")
    install_parser.add_argument(
        "problem_paths", nargs="*", type=str, help="paths to problem source directories"
    )
    install_parser.add_argument(
        "--reinstall",
        action="store_true",
        default=None,
        help="reinstall over an existing version of this problem",
    )
    install_parser.set_defaults(func=install_problems)

    uninstall_parser = subparsers.add_parser(
        "uninstall", help="problem removal - undeploy instances first"
    )
    uninstall_parser.add_argument(
        "problem_names", nargs="*", type=str, help="installed problem names"
    )
    uninstall_parser.set_defaults(func=uninstall_problems)

    deploy_parser = subparsers.add_parser("deploy", help="problem instance deployment")
    deploy_parser.add_argument(
        "-n",
        "--num-instances",
        type=int,
        default=1,
        help="number of instances to deploy (numbers 0 through n-1).",
    )
    deploy_parser.add_argument(
        "-i",
        "--instances",
        action="append",
        type=int,
        help="particular instance(s) to deploy.",
    )
    deploy_parser.add_argument(
        "-d", "--dry", action="store_true", help="don't make persistent changes."
    )
    deploy_parser.add_argument(
        "-r",
        "--redeploy",
        action="store_true",
        help="redeploy instances that have already been deployed",
    )
    deploy_parser.add_argument(
        "-nr",
        "--no-restart",
        action="store_true",
        help="do not restart xinetd after deployment.",
    )
    deploy_parser.add_argument(
        "-c",
        "--containerize",
        action="store_true",
        help="deployment is occuring in a container e.g. with containerize or cmgr",
    )
    deploy_parser.add_argument(
        "-f",
        "--flag-format",
        help="format string for default flag",
    )
    deploy_parser.add_argument(
        "problem_names", nargs="*", type=str, help="installed problem names"
    )
    deploy_parser.set_defaults(func=deploy_problems)

    undeploy_parser = subparsers.add_parser(
        "undeploy", help="problem instance undeployment"
    )
    undeploy_parser.add_argument(
        "-n",
        "--num-instances",
        type=int,
        default=1,
        help="number of instances to undeploy (numbers 0 through n-1).",
    )
    undeploy_parser.add_argument(
        "-i",
        "--instances",
        action="append",
        type=int,
        help="particular instance(s) to undeploy.",
    )
    undeploy_parser.add_argument(
        "problem_names", nargs="*", type=str, help="deployed problem names"
    )
    undeploy_parser.set_defaults(func=undeploy_problems)

    install_bundle_parser = subparsers.add_parser(
        "install-bundle", help="bundle installation"
    )
    install_bundle_parser.add_argument(
        "bundle_path", type=str, help="path to bundle file"
    )
    install_bundle_parser.set_defaults(func=install_bundle)

    uninstall_bundle_parser = subparsers.add_parser(
        "uninstall-bundle", help="bundle removal"
    )
    uninstall_bundle_parser.add_argument(
        "bundle_name", type=str, help="name of installed bundle"
    )
    uninstall_bundle_parser.set_defaults(func=uninstall_bundle)

    status_parser = subparsers.add_parser(
        "status", help="list installed problems and bundles"
    )
    status_parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Show information about all problem instanes.",
    )
    status_parser.add_argument(
        "-p",
        "--problem",
        type=str,
        default=None,
        help="Display status information for a given problem.",
    )
    status_parser.add_argument(
        "-b",
        "--bundle",
        type=str,
        default=None,
        help="Display status information for a given bundle.",
    )
    status_parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        default=None,
        help="Display status information in json format",
    )
    status_parser.add_argument(
        "-e",
        "--errors-only",
        action="store_true",
        help="Only print problems with failing service status.",
    )
    status_parser.set_defaults(func=status)

    clean_parser = subparsers.add_parser("clean", help="clean up problem staging data")
    clean_parser.set_defaults(func=clean)

    publish_parser = subparsers.add_parser(
        "publish", help="export this shell server's state"
    )
    publish_parser.set_defaults(func=publish)

    config_parser = subparsers.add_parser(
        "config", help="view or modify configuration options"
    )
    config_parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        default=False,
        help="Whether to display the configuration options in JSON form or pretty printed. Defaults to False.",
    )
    config_parser.add_argument(
        "config_type",
        choices=["shared", "local"],
        help="Which configuration settings to access: shared (across all "
        + "shell servers), or local (to this shell server)",
    )
    config_parser.set_defaults(func=print_configuration)
    config_subparsers = config_parser.add_subparsers()

    config_set_parser = config_subparsers.add_parser(
        "set", help="Set configuration options"
    )
    config_set_parser.add_argument(
        "-f", "--field", type=str, required=True, help="which field to set"
    )
    config_set_parser.add_argument(
        "-v", "--value", type=str, required=True, help="option's new value"
    )
    config_set_parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        default=False,
        help="interpret the given value as JSON",
    )
    config_set_parser.add_argument(
        "--allow-type-change",
        action="store_true",
        default=False,
        help="allow the supplied field to change types if already specified",
    )
    config_set_parser.set_defaults(func=set_configuration_option)

    ###
    # Containerize
    ###
    containerize_parser = subparsers.add_parser("containerize",
            help="[EXPERIMENTAL] problem instance containerization")
    containerize_parser.add_argument(
        "problem_names", nargs="*", type=str, help="installed problem names"
    )
    containerize_parser.add_argument(
        "-n",
        "--num-instances",
        type=int,
        default=1,
        help="number of instances to deploy (numbers 0 through n-1).",
    )
    containerize_parser.add_argument(
        "-i",
        "--instances",
        action="append",
        type=int,
        help="particular instance(s) to deploy.",
    )
    containerize_parser.add_argument(
        "-f",
        "--flag-format",
        help="format string for default flag",
    )
    containerize_parser.set_defaults(func=containerize_problems)

    args = parser.parse_args()

    if args.colorize == "never":
        coloredlogs.DEFAULT_LEVEL_STYLES = {}
        coloredlogs.DEFAULT_FIELD_STYLES = {}

    coloredlogs.install()

    if args.debug:
        coloredlogs.set_level(logging.DEBUG)
    try:
        if "func" in args:
            args.func(args)
        else:
            parser.print_help()
    except FatalException:
        exit(1)


if __name__ == "__main__":
    main()

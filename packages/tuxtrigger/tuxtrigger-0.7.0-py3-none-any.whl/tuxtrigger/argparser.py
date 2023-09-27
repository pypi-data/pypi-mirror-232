#
# Copyright 2022-present Linaro Limited
#
# SPDX-License-Identifier: MIT
import argparse
from pathlib import Path
from tuxtrigger import __version__


OUTPUT_FILE = Path("share/gitsha.yaml")
PLAN_PATH = Path("share/plans/")
LOG_FILE = Path("log.txt")


def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="TuxTrigger",
        description="TuxTrigger command line tool for controlling changes in repositories",
    )
    parser.add_argument(
        "config", type=Path, help="config yaml file name", action="store"
    )
    parser.add_argument(
        "--sha-compare",
        type=str,
        help="choose compare method",
        default="squad",
        choices=["squad", "yaml"],
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="path for storing output file",
        action="store",
        default=OUTPUT_FILE,
    )
    parser.add_argument(
        "--pre-submit",
        type=Path,
        help="pre-tuxsuite script to run",
        action="store",
    )
    parser.add_argument(
        "-v",
        "--version",
        help="prints current version",
        action="version",
        version=f"%(prog)s, {__version__}",
    )
    parser.add_argument(
        "--submit",
        "-s",
        type=str,
        help="trigger build on change",
        default="change",
        choices=["never", "change", "always"],
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        help="print log to file",
        default=LOG_FILE,
        action="store",
    )
    parser.add_argument(
        "--plan",
        type=Path,
        help="path to plan files",
        default=PLAN_PATH,
        action="store",
    )
    parser.add_argument(
        "--log-level",
        "-l",
        type=str,
        help="set log level to more specific information",
        default="info",
        choices=["debug", "info", "warn", "error"],
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="json output folder path",
        action="store",
    )
    parser.add_argument(
        "--plan-disabled",
        help="disable submiting plan to tuxsuite",
        action="store_false",
    )
    parser.add_argument(
        "--generate-config",
        help="dry-run to show generated config from regex value",
        action="store_true",
    )
    return parser

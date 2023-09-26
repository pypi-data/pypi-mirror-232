#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Bootloader.  All rights reserved.
#
# This software is the confidential and proprietary information of
# Bootloader or one of its subsidiaries.  You shall not disclose this
# confidential information and shall use it only in accordance with the
# terms of the license agreement or other applicable agreement you
# entered into with Bootloader.
#
# BOOTLOADER MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE
# SUITABILITY OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR
# A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.  BOOTLOADER SHALL NOT BE
# LIABLE FOR ANY LOSSES OR DAMAGES SUFFERED BY LICENSEE AS A RESULT OF
# USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

from pathlib import Path
import argparse
import logging
import sys

from majormode.perseus.constant.logging import LOGGING_LEVELS
from majormode.perseus.constant.logging import LOGGING_LEVEL_LITERAL_STRINGS
from majormode.perseus.constant.logging import LoggingLevelLiteral
from majormode.perseus.utils.logging import cast_string_to_logging_level

from bootloader.unity.model.apple_version import AppleAppVersion
from bootloader.unity.utils import project_version

DEFAULT_LOGGING_FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
DEFAULT_LOGGING_LEVEL = LoggingLevelLiteral.info


def cast_string_to_path(path: str) -> Path:
    return Path(path)


def get_console_handler(logging_formatter: logging.Formatter = DEFAULT_LOGGING_FORMATTER) -> logging.StreamHandler:
    """
    Return a logging handler that sends logging output to the system's
    standard output.


    :param logging_formatter: An object `Formatter` to set for this handler
        to appropriately format logging records.


    :return: An instance of the `StreamHandler` class which write logging
        record, appropriately formatted, to the standard output stream.
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging_formatter)
    return console_handler


def parse_arguments() -> argparse.Namespace:
    """
    Convert argument strings to objects and assign them as attributes of
    the namespace.


    :return: An instance `Namespace` corresponding to the populated
        namespace.
    """
    parser = argparse.ArgumentParser(description="Unity project version utility")

    parser.add_argument(
        '--build-number',
        dest='build_number',
        metavar='NUMBER',
        required=False,
        type=int,
        help="Specify the build number of the Unity project."
    )

    parser.add_argument(
        '--logging-level',
        dest='logging_level',
        metavar='LEVEL',
        required=False,
        default=str(LoggingLevelLiteral.info),
        type=cast_string_to_logging_level,
        help=f"Specify the logging level ({', '.join(LOGGING_LEVEL_LITERAL_STRINGS)})."
    )

    parser.add_argument(
        '--path',
        dest='path',
        metavar='PATH',
        required=True,
        type=cast_string_to_path,
        help="Specify the path to the Unity project."
    )

    parser.add_argument(
        '--replace-patch-version',
        action='store_true',
        dest='replace_patch_version',
        required=False,
        help="Indicate whether to replace the patch version of the Unity project"
             "with the specified build number.  This argument MUST be used with"
             "the argument `--build-number`."
    )

    parser.add_argument(
        '--update-version',
        action='store_true',
        dest='update_version',
        required=False,
        help="Indicate whether to update the defined in the Unity project. "
             "This argument MUST be used with the argument `--build-number`."
    )

    return parser.parse_args()


def run():
    arguments = parse_arguments()

    setup_logger(logging_formatter=DEFAULT_LOGGING_FORMATTER, logging_level=arguments.logging_level)

    version = project_version.read_project_version(
        arguments.path,
        build_number=arguments.build_number,
        replace_patch_version=arguments.replace_patch_version,
        require_semantic_versioning=True)

    if arguments.update_version:
        project_version.update_project_version(arguments.path, version)
        ios_version = AppleAppVersion(version, arguments.build_number or 0)
        project_version.update_ios_version(arguments.path, ios_version)

    print(f'{version}+{arguments.build_number}' if arguments else version)


def setup_logger(
        logging_formatter: logging.Formatter = DEFAULT_LOGGING_FORMATTER,
        logging_level: LoggingLevelLiteral = DEFAULT_LOGGING_LEVEL,
        logger_name: str = None) -> logging.Logger:
    """
    Set up a logging handler that sends logging output to the system's
    standard output.


    :param logging_formatter: An object `Formatter` to to appropriately
        format logging records.

    :param logging_level: The logging threshold for this logger.  Logging
        messages which are less severe than this value will be ignored;
        logging messages which have severity level or higher will be
        emitted by whichever handler or handlers service this logger,
        unless a handler’s level has been set to a higher severity level
        than `logging_level`.

    :param logger_name: The name of the logger to add the logging handler
        to.  If `logger_name` is `None`, the function attaches the logging
        handler to the root logger of the hierarchy.


    :return: An object `Logger`.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOGGING_LEVELS[logging_level or DEFAULT_LOGGING_LEVEL])
    logger.addHandler(get_console_handler(logging_formatter=logging_formatter))
    logger.propagate = False
    return logger

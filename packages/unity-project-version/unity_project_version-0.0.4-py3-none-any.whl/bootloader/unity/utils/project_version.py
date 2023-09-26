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
import logging
import re
import os
from pathlib import Path

from majormode.perseus.model.version import Version

from bootloader.unity.model.apple_version import AppleAppVersion


UNITY_CONFIG_PROPERTY_PROJECT_VERSION = 'bundleVersion'

REGEX_PATTERN_PROPERTY_PROJECT_VERSION = rf'^\s*{UNITY_CONFIG_PROPERTY_PROJECT_VERSION}\s*:\s*([a-zA-Z0-9\.\-]+)\s*$'

REGEX_PROPERTY_PROJECT_VERSION = re.compile(REGEX_PATTERN_PROPERTY_PROJECT_VERSION)


def get_settings_file_path(path: Path):
    """
    Return the Unity project's settings file.


    :param path: The root path to the Unity project.


    :return: The file path and name of the Unity project's settings file.
    """
    settings_file_path = Path().joinpath(path.expanduser(), 'ProjectSettings', 'ProjectSettings.asset')
    return settings_file_path


def read_project_version(
        path: Path,
        build_number: int = None,
        replace_patch_version: bool = False,
        require_semantic_versioning: bool = False) -> str or Version:
    """
    Return the project version of a Unity project.

    The version of a Unity project is identified in the attribute
    `bundleVersion` of the settings file `ProjectVersion.asset` located in
    the folder `$ROOT_PATH/ProjectSettings` of the Unity project.


    :param path: The absolute path to the Unity project's root folder.

    :param build_number: The build number of the Unity project.

    :param replace_patch_version: Indicate whether to replace the patch
        version of the Unity project with the specified build number.
        The argument `build_number` MUST be passed  to the function.

    :param require_semantic_versioning: Indicate whether the version
        identified in the configuration file of the Unity project MUST
        comply with Semantic Versioning.


    :return: The version of the Unity project.


    :raise ValueError: If the configuration file of the Unity project has
        not been found, or if the property corresponding to the project
        version is not defined in the configuration file, or if the
        project version is not compliant with Semantic Versioning when
        required.
    """
    if replace_patch_version and build_number is None:
        raise ValueError("A build number MUST be passed to replace the patch version")

    if not path.exists():
        raise ValueError(f"The path {path} doesn't exist")

    settings_file_path = get_settings_file_path(path)

    with open(settings_file_path, 'rt') as fd:
        lines = fd.readlines()

    for line in lines:
        regex_match = REGEX_PROPERTY_PROJECT_VERSION.match(line.strip())
        if regex_match:
            project_version = regex_match.group(1)
            logging.debug(f"Found the version '{project_version}'")

            if require_semantic_versioning:
                project_version = Version(project_version)

            return project_version

    raise ValueError(f"The Unity project has no version defined in the settings file {settings_file_path}")


def update_project_version(
        path: Path,
        version: str or Version) -> None:
    """
    Update the project version of a Unity project.


    The version of a Unity project is identified in the attribute
    `bundleVersion` of the settings file `ProjectSettings.asset` located
    in the folder `$ROOT_PATH/ProjectSettings` of the Unity project.


    :param path: The absolute path to the root folder of a Unity project.

    :param version: The version to write in the Unity project settings
        file.
    """
    if not path.exists():
        raise ValueError(f"The path {path} doesn't exist")

    config_file_path = get_settings_file_path(path)
    with open(config_file_path, 'rt') as fd:
        lines = fd.readlines()

    is_project_version_property_defined = False

    for i in range(len(lines)):
        regex_match = REGEX_PROPERTY_PROJECT_VERSION.match(lines[i].strip())
        if regex_match:
            lines[i] = f'{UNITY_CONFIG_PROPERTY_PROJECT_VERSION}={version}{os.linesep}'
            is_project_version_property_defined = True
            break

    if not is_project_version_property_defined:
        raise ValueError(f"The Unity project has no version defined in the settings file {config_file_path}")

    with open(config_file_path, 'wt') as fd:
        fd.writelines(lines)

#
# Copyright 2022-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import pytest

from pathlib import Path
from tuxtrigger.yamlload import yaml_file_read, create_repo_list

BASE = (Path(__file__) / "..").resolve()

ERROR_PATH = BASE / "./test_files/error_path.yaml"
HAPPY_PATH = BASE / "./test_files/happy_path.yaml"
GITSHA_FILE = BASE / "./test_files/gitsha.yaml"
GITSHA_FILE_2 = BASE / "./test_files/gitsha2.yaml"


@pytest.fixture
def wrong_archive_read():
    try:
        return yaml_file_read(Path("non_existing_file"))
    except FileNotFoundError:
        return None


@pytest.fixture
def correct_archive_read_no_fingerprint():
    return yaml_file_read(GITSHA_FILE_2)


@pytest.fixture
def correct_archive_read():
    return yaml_file_read(GITSHA_FILE)


@pytest.fixture
def repo_setup_error():
    return create_repo_list(yaml_file_read(ERROR_PATH))


@pytest.fixture
def repo_setup_good():
    return create_repo_list(yaml_file_read(HAPPY_PATH))


@pytest.fixture
def squad_group_good():
    return "~non.existing"


@pytest.fixture
def squad_project_good():
    return "example_project"


@pytest.fixture
def lab_good():
    return "https://example_lab"


@pytest.fixture
def lava_test_plans_project_good():
    return "example_lava_test_plans_project"


@pytest.fixture(autouse=True)
def squad_env_setup(monkeypatch):
    monkeypatch.setenv("SQUAD_TOKEN", "some-value")


@pytest.fixture(autouse=True)
def squad_env_host(monkeypatch):
    monkeypatch.setenv("SQUAD_HOST", "https://qa-reports.linaro.org")

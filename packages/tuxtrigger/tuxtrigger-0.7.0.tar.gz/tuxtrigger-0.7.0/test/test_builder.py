#
# Copyright 2022-present Linaro Limited
#
# SPDX-License-Identifier: MIT


import json
from requests import Session
from unittest import mock

import pytest

from pathlib import Path
from tuxtrigger.builder import (
    compare_squad_sha,
    squad_metadata_request,
    tux_console_build,
    tux_console_plan,
    build_result,
    update_squad_metadata,
)
from tuxtrigger.exceptions import SquadException, TuxtriggerException, TuxsuiteException

BASE = (Path(__file__) / "..").resolve()

PLAN = BASE / "test_files/planTest.yaml"
PLAN_FAIL = BASE / "test_files/planTestc.yaml"
JSON_PLAN_RESULT = BASE / "test_files/plan_result.json"
JSON_OUT = BASE / "test_files/"

UID = "2CCI3BkwKdqM4wOOwB5xRRxvOha"
FINGERPRINT = "8fa23329efa65477f077d99e145e4087190a55cc"

PARAMS = {
    "git_repo": "https://gitlab.com/Linaro/lkft/mirrors/stable/linux-stable-rc",
    "git_ref": "master",
    "target_arch": "x86_64",
    "toolchain": "gcc-12",
    "kconfig": "tinyconfig",
}
JSON_DATA = {
    "empty": "no_real_values",
    "uid": "1234",
    "git_repo": "https://gitlab.com/no_real_repo",
    "git_ref": "master",
    "git_sha": "6fae37b8a05e58b6103198e89d12dc0d6d472d92",
    "git_describe": "test-rc",
}
JSON_BUILD_DATA = {
    "state": "provisioning",
    "result": "None",
    "uid": "1234",
    "git_repo": "https://gitlab.com/no_real_repo",
    "git_ref": "master",
    "git_describe": "test-rc",
}

JSON_RESPONSE = """{
"count":1,
"git_sha":"1234",
"tux_fingerprint":"8fa23329efa65477f077d99e145e4087190a55cc",
"results":[
{
"metadata":"https://www.example_metadata.pl",
"id":1234
}
]
}"""


class MockedStdout:
    def __init__(self, returncode, stdout, stderr=None) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class MockedSession:
    def __init__(self, status_code, content, ok=True) -> None:
        self.status_code = status_code
        self.content = content
        self.ok = ok


@mock.patch("tuxtrigger.builder.subprocess.run")
@mock.patch("tempfile.NamedTemporaryFile")
def test_tux_console_build(mock_temp_file, mock_run):
    build = MockedStdout(returncode=0, stdout=JSON_DATA)
    mock_run.return_value = build
    with open(BASE / "test_files/test.json", "r") as temp_file:
        mock_temp_file.return_value.__enter__.return_value = temp_file
        result = tux_console_build(**PARAMS)
    assert result == JSON_DATA["uid"]

    build_error = MockedStdout(returncode=1, stdout="", stderr="Tuxsuite Failure")
    mock_run.return_value = build_error
    with pytest.raises(TuxsuiteException) as exc:
        tux_console_build(**PARAMS)
    assert "Tuxsuite not build repo" in str(exc)


@mock.patch(
    "tuxtrigger.builder.subprocess.run",
    side_effect=TuxsuiteException("*** Tuxsuite not build repo"),
)
def test_tux_console_build_error(mock_run):
    build = MockedStdout(returncode=1, stdout=None)
    mock_run.return_value = build
    with pytest.raises(TuxsuiteException) as ex:
        tux_console_build(**PARAMS)
    assert "Tuxsuite not build" in str(ex.value)


@mock.patch("tuxtrigger.builder.subprocess.run")
def test_tux_console_plan_error(
    mock_run,
    squad_group_good,
    squad_project_good,
    lab_good,
    lava_test_plans_project_good,
):
    build = MockedStdout(returncode=1, stdout=JSON_DATA)
    mock_run.return_value = build
    with pytest.raises(TuxtriggerException) as exc_tuxtrigger:
        tux_console_plan(
            None,
            PLAN,
            squad_group_good,
            squad_project_good,
            JSON_OUT,
            FINGERPRINT,
            lab_good,
            lava_test_plans_project_good,
        )

    assert "*** Not able to submit plan" in str(exc_tuxtrigger)
    with pytest.raises(TuxsuiteException) as exc_tuxsuite:
        tux_console_plan(
            JSON_DATA,
            PLAN,
            squad_group_good,
            squad_project_good,
            JSON_OUT,
            FINGERPRINT,
            lab_good,
            lava_test_plans_project_good,
        )
    assert "Submiting Plan for example_project_test-rc failed" in str(exc_tuxsuite)


@mock.patch("tuxtrigger.builder.subprocess.run")
@mock.patch("tempfile.NamedTemporaryFile")
def test_tux_console_plan(
    mock_temp_file,
    mock_run,
    squad_group_good,
    squad_project_good,
    lab_good,
    lava_test_plans_project_good,
):
    build = MockedStdout(returncode=0, stdout=JSON_DATA)
    mock_run.return_value = build
    with open(BASE / "test_files/test.json", "r") as test_file:
        mock_temp_file.return_value.__enter__.return_value = test_file
        tux_console_plan(
            JSON_DATA,
            PLAN_FAIL,
            squad_group_good,
            squad_project_good,
            JSON_OUT,
            FINGERPRINT,
            lab_good,
            lava_test_plans_project_good,
        )


@mock.patch("tuxtrigger.builder.subprocess.run")
def test_build_result(mock_run):
    build = MockedStdout(returncode=0, stdout=json.dumps(JSON_BUILD_DATA))
    mock_run.return_value = build
    json_output = build_result(UID)
    mock_run.assert_called_once_with(
        ["tuxsuite", "build", "get", UID, "--json"], stdout=-1, stderr=-1, text=True
    )
    assert build_result(None) is None
    assert JSON_BUILD_DATA == json_output


@mock.patch("tuxtrigger.builder.subprocess.run")
def test_build_result_error(mock_run):
    build = MockedStdout(returncode=1, stdout="Oops!")
    mock_run.return_value = build
    with pytest.raises(TuxsuiteException) as exc:
        build_result(UID)
    assert "*** Build result for UID:2CCI3BkwKdqM4wOOwB5xRRxvOha failed" in str(exc)


def test_update_squad_metadata_error(squad_project_good):
    with pytest.raises(TuxtriggerException) as exc:
        update_squad_metadata(JSON_DATA, None, squad_project_good, FINGERPRINT)
    assert "SQUAD config is not available!" in str(exc)


@mock.patch.object(Session, "post")
def test_update_squad_metadata(mock_session, squad_group_good, squad_project_good):
    session_ok = MockedSession(status_code=200, content=JSON_RESPONSE, ok=True)
    mock_session.return_value = session_ok
    update_result = update_squad_metadata(
        JSON_DATA, squad_group_good, squad_project_good, FINGERPRINT
    )
    assert update_result == 0


@mock.patch.object(Session, "get")
def test_squad_sha_request(mock_session):
    session_ok = MockedSession(status_code=200, content=JSON_RESPONSE)
    mock_session.return_value = session_ok
    squad_sha = squad_metadata_request("1111", "tuxtrigger")
    assert squad_sha == ("8fa23329efa65477f077d99e145e4087190a55cc", "1234")


@mock.patch.object(Session, "get")
def test_squad_sha_request_fail(mock_session):
    session_fail = MockedSession(status_code=404, content=(None, None))
    mock_session.return_value = session_fail
    with pytest.raises(SquadException) as exc:
        squad_metadata_request("1112", "tuxtrigger")
    assert "SQUAD response error - (get latest build) 404" in str(exc)

    assert squad_metadata_request(None, None) == (None, None)


@mock.patch("tuxtrigger.builder.squad_metadata_request")
def test_compare_squad_sha(mock_sha):
    mock_sha.return_value = ("1234", "1234")
    assert compare_squad_sha("1111", "tuxtrigger", "1234") is False
    assert compare_squad_sha("1112", "tuxtrigger", "5678") is True


def test_compare_squad_sha_none():
    assert compare_squad_sha(None, None, "1234") is True

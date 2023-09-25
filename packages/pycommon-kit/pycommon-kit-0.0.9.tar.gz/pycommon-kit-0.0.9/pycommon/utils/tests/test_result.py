import pytest
import unittest

from pycommon.utils.result import Result


@pytest.fixture(name="success_result")
def get_success_result() -> Result:
    return Result.success("success_data")


@pytest.fixture(name="failure_result")
def get_failure_result() -> Result:
    return Result.failure("test_error")


@pytest.fixture(name="server_error_result")
def get_server_error_result() -> Result:
    return Result.server_error("test_server_error")


class TestResult:
    def test_success_result(self, success_result) -> None:
        assert success_result.is_success() is True
        assert success_result.is_failure() is False
        assert success_result.error is None
        assert success_result.data == "success_data"
        assert success_result.status == "success"

    def test_failure_result(self, failure_result) -> None:
        assert failure_result.is_success() is False
        assert failure_result.is_failure() is True
        assert failure_result.data is None
        assert failure_result.error == "test_error"
        assert failure_result.status == "failure"

    def test_server_error_result(self, server_error_result) -> None:
        assert server_error_result.is_success() is False
        assert server_error_result.is_failure() is True
        assert server_error_result.data is None
        assert server_error_result.error == "test_server_error"
        assert server_error_result.status == "failure"

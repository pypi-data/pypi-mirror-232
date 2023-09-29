import os
import pytest
from deepaix.common.utils import (
    create_dir_if_not_exists,
    check_path_exists,
    setup_dir_for_file_path,
    cleanup_string,
    send_mac_native_notification,
    nested_dataclass,
)


def test_create_dir_if_not_exists():
    path = "test_dir"
    create_dir_if_not_exists(path)
    assert os.path.exists(path)
    os.rmdir(path)


def test_check_path_exists():
    path = "test_dir"
    os.makedirs(path)
    assert check_path_exists(path)
    os.rmdir(path)


def test_setup_dir_for_file_path():
    file_path = "test_dir/test_file.txt"
    setup_dir_for_file_path(file_path)
    assert os.path.exists("test_dir")
    os.rmdir("test_dir")


def test_cleanup_string():
    s = "  this is \ta test\n"
    cleaned_s = cleanup_string(s)
    assert cleaned_s == "thisisatest"


@pytest.mark.skip(reason="This function depends on the operating system")
def test_send_mac_native_notification():
    send_mac_native_notification("This is a test message")


@nested_dataclass
class Inner:
    x: int


@nested_dataclass
class Outer:
    inner: Inner


def test_nested_dataclass():
    obj = Outer(inner={"x": 1})
    assert obj.inner.x == 1

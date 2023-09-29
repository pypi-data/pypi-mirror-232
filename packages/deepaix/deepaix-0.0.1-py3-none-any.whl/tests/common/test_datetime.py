from datetime import datetime
import pytz
import time
from unittest.mock import patch

from deepaix.common.datetime import (
    get_datetime_from_unixtime,
    get_timestamp,
    get_datetime_by_date_trs,
    get_jst_now,
)


def test_get_datetime_from_unixtime():
    unix_time = time.time()
    expected_dt = datetime.fromtimestamp(unix_time)
    assert get_datetime_from_unixtime(unix_time) == expected_dt


def test_get_timestamp():
    now = datetime.now()
    assert get_timestamp() == now.strftime("%Y%m%d-%H%M")


def test_get_datetime_by_date_trs():
    date_str = "20210925"
    expected_dt = datetime.strptime(date_str, "%Y%m%d")
    assert get_datetime_by_date_trs(date_str) == expected_dt


@patch("deepaix.common.datetime.datetime")
def test_get_jst_now(mock_datetime):
    mock_datetime.now.return_value = datetime(2023, 9, 28, 9, 13, 53, 297007)
    japan_tz = pytz.timezone("Asia/Tokyo")
    expected_datetime = japan_tz.localize(datetime(2023, 9, 28, 9, 13, 53, 297007))
    assert get_jst_now() == expected_datetime

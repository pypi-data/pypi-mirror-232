from datetime import datetime
import pytz


TIME_FORMAT = "%Y%m%d-%H%M"
DATE_FORMAT = "%Y%m%d"
MONTH_FORMAT = "%Y%m"


def get_datetime_from_unixtime(d: float):
    return datetime.fromtimestamp(d)


def get_timestamp(format: str = TIME_FORMAT) -> str:
    return datetime.now().strftime(format)


def get_today() -> str:
    return get_timestamp(DATE_FORMAT)


def get_datetime_by_date_trs(d: str) -> datetime:
    return datetime.strptime(d, "%Y%m%d")


def get_jst_now() -> datetime:
    japan_tz = pytz.timezone("Asia/Tokyo")
    return japan_tz.localize(datetime.now())

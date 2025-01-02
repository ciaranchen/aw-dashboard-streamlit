import datetime
import pytz


def date2timestamp(var_datetime, timezone):
    """
    将日期转换为纳秒时间戳
    """
    localtime = pytz.timezone(timezone).localize(var_datetime)
    int_stamp = int(localtime.timestamp()) * 1e9
    return int_stamp


def timestamp2datetime(timestamp, timezone):
    # 使用 datetime 模块将时间戳转换为 datetime 对象
    return datetime.datetime.fromtimestamp(timestamp / 1000000000, pytz.timezone(timezone))

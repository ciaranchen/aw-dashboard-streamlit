import datetime
import pytz


def date2timestamp(date, timezone, hour_offset):
    """
    将日期转换为时间戳并添加小时偏移量
    """
    date_time = datetime.datetime.combine(date, datetime.time())
    localtime = pytz.timezone(timezone).localize(date_time) + datetime.timedelta(hours=hour_offset)
    int_stamp = int(localtime.timestamp())
    return int_stamp * 1000000000


def timestamp2datetime(timestamp, timezone):
    # 使用 datetime 模块将时间戳转换为 datetime 对象
    return datetime.datetime.fromtimestamp(timestamp / 1000000000, pytz.timezone(timezone))


def convert_seconds_to_hhmmss(seconds):
    """
    此函数将输入的秒数转换为 "HH:MM:SS" 格式的时间字符串。

    参数:
    seconds (int): 要转换的秒数。

    返回:
    str: 格式为 "HH:MM:SS" 的时间字符串。
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return "{}h {:02d}m {:02d}s".format(int(hours), int(minutes), int(seconds))

import datetime

import pandas as pd
import pytz
import streamlit as st
from pyecharts.charts import Bar
from pyecharts import options as opts



from database import ActivityWatchDataBase
from utils import date2timestamp, timestamp2datetime


def show_timeline():
    st.title("Data Classification and Visualization with RuleNode")
    db = ActivityWatchDataBase()

    # 日期选择器
    start_date = st.date_input("Date", datetime.date(2024, 12, 1))

    # 高级选项：隐藏在 Collapse 栏目中的小时偏移量下拉菜单
    with st.expander("Advanced Options"):
        hour_offset = st.selectbox("Hour Offset", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], index=0)
        timezone = st.selectbox("Timezone", pytz.all_timezones, index=pytz.all_timezones.index("Asia/Shanghai"))

    start_timestamp = date2timestamp(start_date, timezone, hour_offset)
    end_date = start_date + datetime.timedelta(days=1)
    end_timestamp = date2timestamp(end_date, timezone, hour_offset)
    events_data = db.fetch_events_data(
        starttime=start_timestamp,
        endtime=end_timestamp,
        limit=200)

    print(timestamp2datetime(pd.Series(start_timestamp), timezone))

    # 将获取的数据转换为DataFrame，方便后续处理
    df = pd.DataFrame(events_data)
    df['start_datetime'] = timestamp2datetime(df['starttime'], timezone)
    df['end_datetime'] = timestamp2datetime(df['endtime'], timezone)

    bar = Bar()
    # 提取 bucketrow 作为 x 轴数据
    x_axis = df["bucketrow"].tolist()
    bar.add_xaxis(x_axis)

    grouped = df.groupby('bucketrow')
    for group in grouped:
        print(group)

    # 计算每个任务的时长
    durations = []
    for index, row in df.iterrows():
        start = pd.to_datetime(row["starttime"])
        end = pd.to_datetime(row["endtime"])
        duration = (end - start).total_seconds()
        durations.append(duration)

    # 添加数据
    bar.add_yaxis(
        "Duration",
        durations,
        label_opts=opts.LabelOpts(position="inside")
    )
    # 设置全局配置项
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="Bar Chart representing Gantt-like data"),
        xaxis_opts=opts.AxisOpts(name="bucketrow"),
        yaxis_opts=opts.AxisOpts(name="Duration (seconds)"),
    )

    st_pyecharts = st.components.v1.html(bar.render_embed(), height=400)


if __name__ == '__main__':
    show_timeline()

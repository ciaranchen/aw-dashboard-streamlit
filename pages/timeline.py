import datetime

import pandas as pd
import pytz
import streamlit as st
import plotly.express as px

from database import ActivityWatchDataBase
from rule_node import ClassifyMethod
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
        endtime=end_timestamp)

    # 对数据进行分类
    cm = ClassifyMethod()
    classified_data = cm.classify_data(events_data)

    # 将获取的数据转换为DataFrame，方便后续处理
    df = pd.DataFrame(events_data)
    df['start_datetime'] = timestamp2datetime(df['starttime'], timezone)
    df['end_datetime'] = timestamp2datetime(df['endtime'], timezone)
    df['category'] = classified_data

    fig = px.timeline(df, x_start='start_datetime', x_end='end_datetime', y='name', color='category')
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig)


if __name__ == '__main__':
    show_timeline()

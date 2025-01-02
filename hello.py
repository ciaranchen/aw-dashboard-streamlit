import datetime

import pytz
import streamlit as st

from database import ActivityWatchDataBase
from pages.activity import build_sunburst_graph
from rule_node import ClassifyMethod

from utils import date2timestamp


def main():
    st.title("Activity")
    db = ActivityWatchDataBase()

    # 日期选择器
    start_date = st.date_input("Start Date", datetime.date(2024, 12, 1))
    end_date = st.date_input("End Date", datetime.date(2024, 12, 15))

    # 高级选项：隐藏在 Collapse 栏目中的小时偏移量下拉菜单
    with st.expander("Advanced Options"):
        hour_offset = st.selectbox("Hour Offset", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], index=0)
        timezone = st.selectbox("Timezone", pytz.all_timezones, index=pytz.all_timezones.index("Asia/Shanghai"))

    buckets_data = db.fetch_bucket_data()
    # 将数据转换为列表的列表，以便 st.data_editor 显示
    # if buckets_data:
    buckets_data.insert(0, 'Select', buckets_data['type'] != 'afkstatus')

    # 使用 st.data_editor 显示表格并添加一个多选列
    selected_buckets_data = st.data_editor(
        buckets_data,
        column_config={
            "Select": st.column_config.CheckboxColumn("Select", help="Select rows")
        },
        hide_index=True,
        disabled=[c for c in buckets_data.columns if c != 'Select']
    )

    # 存储选中的行
    selected_buckets_id = selected_buckets_data[selected_buckets_data['Select']]['id'].to_list()
    start_timestamp = date2timestamp(start_date, timezone, hour_offset)
    end_timestamp = date2timestamp(end_date, timezone, hour_offset)
    # print(start_timestamp)
    # print(end_timestamp)
    events_data = db.fetch_events_data(
        starttime=start_timestamp,
        endtime=end_timestamp,
        bucket_ids=selected_buckets_id)
    #
    # print(events_data)
    cm = ClassifyMethod('rules.json')
    cm.classify_data(events_data)
    build_sunburst_graph(events_data, cm.root)


if __name__ == '__main__':
    main()

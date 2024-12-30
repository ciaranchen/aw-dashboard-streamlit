import datetime

import pytz
import streamlit as st
import plotly.express as px

from database import ActivityWatchDataBase
from rule_node import ClassifyMethod
from utils import date2timestamp


def show_activity():
    st.title("Data Classification and Visualization with RuleNode")
    db = ActivityWatchDataBase()

    # 日期选择器
    start_date = st.date_input("Start Date", datetime.date(2024, 12, 1))
    end_date = st.date_input("End Date", datetime.date(2024, 12, 15))

    # 高级选项：隐藏在 Collapse 栏目中的小时偏移量下拉菜单
    with st.expander("Advanced Options"):
        hour_offset = st.selectbox("Hour Offset", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], index=0)
        timezone = st.selectbox("Timezone", pytz.all_timezones, index=pytz.all_timezones.index("Asia/Shanghai"))

    rows = db.fetch_bucket_data()
    # 将数据转换为列表的列表，以便 st.data_editor 显示
    if rows:
        column_names = ['Select'] + list(rows[0].keys())
        bucket_data = [[True] + list(row) for row in rows]

        # 使用 st.data_editor 显示表格并添加一个多选列
        edited_data = st.data_editor(
            bucket_data,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Select rows",
                    default=True,
                )
            },
            hide_index=True,
            disabled=column_names[1:]
        )

        # 存储选中的行
        selected_rows = []
        for i, row in enumerate(edited_data):
            if row[0]:  # 假设第一列是 Select 列
                selected_rows.append(row[1:])  # 排除 Select 列

    button_click = st.button("Query")
    if button_click:
        if rows:
            selected_rows = [row[1] for row in edited_data if row[0]]
        else:
            selected_rows = None
        start_timestamp = date2timestamp(start_date, timezone, hour_offset)
        end_timestamp = date2timestamp(end_date, timezone, hour_offset)
        # print(start_timestamp)
        # print(end_timestamp)
        events_data = db.fetch_events_data(
            starttime=start_timestamp,
            endtime=end_timestamp,
            bucket_ids=selected_rows)

        # 对数据进行分类
        cm = ClassifyMethod()
        classified_data = cm.classify_data(events_data)

        # 绘制 Sunburst 图
        sunburst_data = cm.build_sunburst_data(events_data, classified_data)

        fig = px.sunburst(
            sunburst_data,
            names="names",
            parents='parents',
            values='durations'
        )
        st.plotly_chart(fig)


if __name__ == '__main__':
    show_activity()

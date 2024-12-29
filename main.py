import datetime

import pytz
import streamlit as st
from pyecharts.charts import Sunburst
from pyecharts import options as opts

from database import ActivityWatchDataBase
from rule_node import RuleNode
from rules import root


def main():
    st.title("Data Classification and Visualization with RuleNode")
    db = ActivityWatchDataBase()

    # 日期选择器
    start_date = st.date_input("Start Date", datetime.date(2024, 12, 1))
    end_date = st.date_input("End Date", datetime.date(2024, 12, 15))

    # 高级选项：隐藏在 Collapse 栏目中的小时偏移量下拉菜单
    with st.expander("Advanced Options"):
        hour_offset = st.selectbox("Hour Offset", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], index=0)
        timezone = st.selectbox("Timezone", pytz.all_timezones, index=pytz.all_timezones.index("UTC"))

    # 将日期转换为字符串
    # 将日期转换为时间戳并添加小时偏移量、
    def date2timestamp(date):
        date_time = datetime.datetime.combine(date, datetime.time())
        localtime = pytz.timezone(timezone).localize(date_time) + datetime.timedelta(hours=hour_offset)
        int_stamp = int(localtime.timestamp())
        return int_stamp * 1000000000

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
        start_timestamp = date2timestamp(start_date)
        end_timestamp = date2timestamp(end_date)
        # print(start_timestamp)
        # print(end_timestamp)
        events_data = db.fetch_events_data(
            starttime=start_timestamp,
            endtime=end_timestamp,
            bucket_ids=selected_rows)

        # 对数据进行分类
        classified_data = RuleNode.classify_data(events_data, root)

        # 绘制 Sunburst 图
        sunburst_data = RuleNode.build_sunburst_data(events_data, classified_data, root)

        # 使用pyecharts绘制饼图
        sunburst = Sunburst()
        sunburst.add("", sunburst_data)
        sunburst.set_global_opts(title_opts=opts.TitleOpts(title="Data Classification Result"))
        st_pyecharts = st.components.v1.html(sunburst.render_embed(), height=400)


if __name__ == "__main__":
    main()

import datetime

import pandas as pd
import pytz
import streamlit as st

from database import ActivityWatchDataBase
from charts import show_sunburst_chart, show_timeline_chart, show_area_chart
from category import Category
from utils import date2timestamp

db = ActivityWatchDataBase()


def main():
    st.title("Activity")

    # 日期选择器
    start_date = st.date_input("Start Date", datetime.date(2024, 12, 1))
    end_date = st.date_input("End Date", datetime.date(2024, 12, 5))

    # 高级选项：隐藏在 Collapse 栏目中的小时偏移量下拉菜单
    with st.expander("Advanced Options"):
        hour_offset = st.selectbox("Hour Offset", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], index=0)
        timezone = st.selectbox("Timezone", pytz.all_timezones, index=pytz.all_timezones.index("Asia/Shanghai"))
        # 折线图所需的频率
        freq = st.selectbox('Select resampling frequency:',
                            # 可选择的频率：小时、三小时、天、三天、周、月
                            ['h', '3h', 'D', '3D', 'W', 'M'], index=1)

    start_datetime = datetime.datetime.combine(start_date, datetime.time()) + datetime.timedelta(hours=hour_offset)
    end_datetime = datetime.datetime.combine(end_date, datetime.time()) + datetime.timedelta(hours=hour_offset)
    start_timestamp = date2timestamp(start_datetime, timezone)
    end_timestamp = date2timestamp(end_datetime, timezone)

    buckets_data = db.fetch_bucket_data()
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

    button = st.button('Query')
    if button:
        events_data = db.fetch_events_data(
            starttime=start_timestamp,
            endtime=end_timestamp,
            bucket_ids=selected_buckets_id)
        events_data['start_datetime'] = pd.to_datetime(events_data['starttime'], unit='ns', utc=True).dt.tz_convert(
            timezone)
        events_data['end_datetime'] = pd.to_datetime(events_data['endtime'], unit='ns', utc=True).dt.tz_convert(
            timezone)
        # 计算 duration
        events_data['duration'] = events_data['end_datetime'] - events_data['start_datetime']

        root = Category.load_from_yaml('categories.yaml')
        Category.categorize_data(root, events_data)
        category_duration = Category.calc_category_duration(root, events_data)

        show_sunburst_chart(category_duration, root)
        show_timeline_chart(events_data, root, start_datetime, end_datetime)
        show_area_chart(events_data, root, freq)


if __name__ == '__main__':
    main()

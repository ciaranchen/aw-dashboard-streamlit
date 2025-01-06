import datetime

import pandas as pd
import pytz
import streamlit as st

from database import ActivityWatchDataBase
from charts import show_sunburst_chart, show_timeline_chart, show_area_chart
from category import Category
from duration_list import show_events_list, show_categories_list
from utils import date2timestamp

db = ActivityWatchDataBase()


def main():
    st.set_page_config(layout='wide')
    st.title("Activity")

    with st.form('activity_form'):
        # 日期选择器
        date_col1, date_col2 = st.columns(2)
        today = datetime.date.today()
        first_day_of_month = today.replace(day=1)
        start_date = date_col1.date_input("Start Date", first_day_of_month, max_value=today)
        end_date = date_col2.date_input("End Date", today, max_value=today, min_value=start_date)

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
        button = st.form_submit_button("Query")

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
        st.session_state['events_data'] = events_data
        st.session_state['category_duration'] = category_duration
        st.session_state['displayed_events'] = []
        st.session_state['displayed_categories'] = []

    if 'events_data' in st.session_state:
        root = Category.load_from_yaml('categories.yaml')
        events_data = st.session_state['events_data']
        category_duration = st.session_state['category_duration']

        show_timeline_chart(events_data, root, start_datetime, end_datetime)
        show_area_chart(events_data, root, freq)

        col1, col2, col3 = st.columns(3)
        with col1:
            show_events_list(events_data)
        with col2:
            show_categories_list(category_duration)
        with col3:
            show_sunburst_chart(category_duration, root)


if __name__ == '__main__':
    main()

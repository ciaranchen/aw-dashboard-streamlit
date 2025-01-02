import datetime

import pandas as pd
import pytz
import streamlit as st
import plotly.express as px

from database import ActivityWatchDataBase
from category import ClassifyMethod, Category
from utils import date2timestamp


def show_sunburst_chart(data, root):
    def add_duration(leaf_node: Category, duration):
        rule_durations[leaf_node.id] += duration
        if leaf_node.parent:
            add_duration(leaf_node.parent, duration)

    rule_lists = {rule.id: rule for rule in root.flatten}
    rule_durations = {rule.id: pd.Timedelta(0) for rule in rule_lists.values()}
    # 按 category 分组并计算 duration 的总和
    duration_by_category = data.groupby('category')['duration'].sum()
    # print(duration_by_category)
    for category, duration in duration_by_category.items():
        add_duration(rule_lists[category], duration)

    names = []
    parents = []
    durations = []
    colors = []
    for rid, rule in rule_lists.items():
        if rule is root:
            continue
        names.append(rule.extend_name)
        # 除了root节点之外其它都有parent。
        parents.append(rule.parent.extend_name)
        durations.append(rule_durations[rid])
        colors.append(rule.parent.color)
    categorized_duration = pd.Timedelta(0)
    for child in root.children:
        categorized_duration += rule_durations[child.id]
    # handle uncategories
    names.append('uncategories')
    parents.append(root.extend_name)
    durations.append(rule_durations[root.id] - categorized_duration)
    colors.append(root.color)
    # handle root
    names.append(root.extend_name)
    parents.append(None)
    durations.append(rule_durations[root.id])
    colors.append('rgba(255,255,255,1)')

    fig = px.sunburst({
        "names": names,
        "parents": parents,
        "durations": durations,
        "colors": colors
    },
        names="names",
        parents='parents',
        values='durations',
        color="colors"
    )

    st.plotly_chart(fig)


def show_timeline_chart(events_data, root, start_datetime, end_datetime):
    fig = px.timeline(events_data, x_start='start_datetime', x_end='end_datetime', y='name', color='category')
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=[start_datetime, end_datetime])
    st.plotly_chart(fig)

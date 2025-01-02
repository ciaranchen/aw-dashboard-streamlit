import pandas as pd
import streamlit as st
import plotly.express as px


def show_sunburst_chart(category_durations, root):
    rule_lists = {rule.id: rule for rule in root.flatten}

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
        durations.append(category_durations.iloc[rid, 0])
        colors.append(rule.color)
    categorized_duration = pd.Timedelta(0)
    for child in root.children:
        categorized_duration += category_durations.iloc[child.id, 0]
    # handle uncategories
    names.append('uncategories')
    parents.append(root.extend_name)
    durations.append(category_durations.iloc[root.id, 0] - categorized_duration)
    colors.append(root.color)

    d_values = [d.value for d in durations]

    colors_map = {c: c for c in colors}
    print(colors)

    fig = px.sunburst(
        names=names,
        parents=parents,
        values=durations,
        color=colors,
        color_discrete_map={c: c for c in colors}
    )

    st.plotly_chart(fig)


def show_timeline_chart(events_data, root, start_datetime, end_datetime):
    fig = px.timeline(events_data, x_start='start_datetime', x_end='end_datetime', y='name', color='category')
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=[start_datetime, end_datetime])
    st.plotly_chart(fig)

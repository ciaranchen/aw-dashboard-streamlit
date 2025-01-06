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
    categorized_duration = sum([category_durations.iloc[child.id, 0] for child in root.children], start=pd.Timedelta(0))
    # handle uncategories
    names.append('uncategories')
    parents.append(root.extend_name)
    durations.append(category_durations.iloc[root.id, 0] - categorized_duration)
    colors.append(root.color)

    # handle fake root
    root_name = '_'
    names.append(root_name)
    for i, p in enumerate(parents):
        if len(p) == 0:
            parents[i] = root_name
    parents.append('')
    durations.append(pd.Timedelta(0))
    colors.append('rgb(255,255,255,0)')

    fig = px.sunburst(
        names=names,
        parents=parents,
        values=durations,
        color=colors,
        color_discrete_map={c: c for c in colors}
    )
    st.title('Sunburst')
    st.plotly_chart(fig)


def show_timeline_chart(events_data, root, start_datetime, end_datetime):
    """
    显示一个时间轴图表，展示事件的开始时间、结束时间、名称和类别。

    参数:
    events_data (DataFrame): 包含事件数据的 DataFrame。
    root (TreeNode): 根节点，用于获取颜色映射。
    start_datetime (datetime): 时间轴的开始时间。
    end_datetime (datetime): 时间轴的结束时间。

    返回:
    None
    """
    color_map = {rule.extend_name: rule.color for rule in root.flatten}

    fig = px.timeline(events_data,
                      title='Time Line',
                      x_start='start_datetime', x_end='end_datetime', y='bucket_name',
                      range_x=[start_datetime, end_datetime],
                      color='category_name',
                      hover_name='category_name',
                      color_discrete_sequence=list(color_map.values()))

    fig.update_yaxes(autorange="reversed")
    fig.update_traces(marker_showscale=False)
    st.plotly_chart(fig)


def show_treemap_chart(events_data):
    pass


def show_area_chart(events_data, root, freq):
    # 透视表将 category 列转为列，使用 duration 填充数据
    events_data['duration_seconds'] = events_data['duration'].dt.total_seconds()
    pivot_df = events_data.pivot_table(index='start_datetime', columns='category_name', values='duration_seconds',
                                       aggfunc='sum', fill_value=0)

    # 重采样透视表
    if freq == 'h':
        resampled_pivot_df = pivot_df.resample('h').sum()
    elif freq == '3h':
        resampled_pivot_df = pivot_df.resample('3h').sum()
    elif freq == 'D':
        resampled_pivot_df = pivot_df.resample('D').sum()
    elif freq == '3D':
        resampled_pivot_df = pivot_df.resample('3D').sum()
    elif freq == 'W':
        resampled_pivot_df = pivot_df.resample('W').sum()
    elif freq == 'M':
        resampled_pivot_df = pivot_df.resample('M').sum()
    else:
        raise Exception()

    # print(resampled_pivot_df.columns)
    category_colors = {rule.extend_name: rule.color for rule in root.flatten}
    colors = [category_colors[c] for c in resampled_pivot_df.columns]
    # color = resampled_pivot_df['category'].apply(lambda x: color_map[x])
    # print(color)
    # color_map = {rule.color: rule.color for rule in root.flatten}

    # 绘制堆叠折线图
    fig = px.area(resampled_pivot_df,
                  title=f'Durations by Category ({freq})',
                  color_discrete_sequence=colors
                  )
    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Duration',
        legend_title='Category'
    )
    st.plotly_chart(fig)

import streamlit as st
from pyecharts.charts import Sunburst
from pyecharts import options as opts

from database import fetch_data
from rule_node import RuleNode
from rules import root


def main():
    st.title("Data Classification and Visualization with RuleNode")

    # 模拟数据
    data = fetch_data(starttime=1732996800000000000, endtime=1735156800000000000)

    # 对数据进行分类
    classified_data = RuleNode.classify_data(data, root)

    # 绘制 Sunburst 图
    sunburst_data = RuleNode.build_sunburst_data(classified_data, root)
    # print(sunburst_data)
    # return

    # 使用pyecharts绘制饼图
    sunburst = Sunburst()
    sunburst.add("", [sunburst_data])
    sunburst.set_global_opts(title_opts=opts.TitleOpts(title="Data Classification Result"))
    st_pyecharts = st.components.v1.html(sunburst.render_embed(), height=400)


if __name__ == "__main__":
    main()

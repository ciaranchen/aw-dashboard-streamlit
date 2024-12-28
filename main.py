import streamlit as st
from pyecharts.charts import Pie
from pyecharts import options as opts
from rule_node import RuleNode


def main():
    st.title("Data Classification and Visualization with RuleNode")

    # 模拟数据
    data = [
        {"id": 1, "value": 100},
        {"id": 2, "value": 200},
        {"id": 3, "value": 300}
    ]

    # 创建规则节点
    root = RuleNode("root", [], "#000000", 1)
    category1 = RuleNode("category1", ["Category1"], "#FF0000", 0.5, "item['value'] > 150", root)
    subcategory1_1 = RuleNode("subcategory1_1", ["Subcategory1", "Subcategory1.1"], "#FFA500", 0.3,
                              "item['value'] > 250", category1)
    subcategory1_2 = RuleNode("subcategory1_2", ["Subcategory1", "Subcategory1.2"], "#FFFF00", 0.2,
                              "item['value'] > 180", category1)

    category2 = RuleNode("category2", ["Category2"], "#00FF00", 0.3, "item['value'] <= 150", root)
    subcategory2_1 = RuleNode("subcategory2_1", ["Subcategory2", "Subcategory2.1"], "#008000", 0.6,
                              "item['value'] <= 120", category2)
    subcategory2_2 = RuleNode("subcategory2_2", ["Subcategory2", "Subcategory2.2"], "#0000FF", 0.4,
                              "item['value'] <= 140", category2)

    uncategorized = RuleNode("uncategorized", ["uncategorized"], "#808080", 0.2, None, root)

    # 对数据进行分类
    classified_data = RuleNode.classify_data(data, root)

    # 准备饼图数据
    pie_data = [(item["category"][0], item["weight"]) for item in classified_data]

    # 使用pyecharts绘制饼图
    pie_chart = Pie()
    pie_chart.add("", pie_data)
    pie_chart.set_global_opts(title_opts=opts.TitleOpts(title="Data Classification Result"))
    st_pyecharts = st.components.v1.html(pie_chart.render_embed(), height=400)


if __name__ == "__main__":
    main()

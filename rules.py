from rule_node import RuleNode

root = RuleNode([], "#000000", 1)
category1 = RuleNode(["Category1"], "#FF0000", 0.5, root, '$.($contains(hostname, "PC"))')
category2 = RuleNode(["Category2"], "#00FF00", 0.5, root, '$.($contains(hostname, "TB"))')
category3 = RuleNode(["Category3"], "#0000FF", 0.5, root, '$.($contains(hostname, "Dell"))')

RuleNode(["Category1", "Web"], "#FFA500", 0.3, category1,
         '$.($contains(hostname, "PC") and type="web.tab.current")')
RuleNode(["Category1", "Window"], "#FFFF00", 0.2, category1,
         '$.($contains(hostname, "PC") and type="currentwindow")')

# category2 = RuleNode(["Category2"], "#00FF00", 0.3, "value <= 150", root)
# subcategory2_1 = RuleNode(["Subcategory2", "Subcategory2.1"], "#008000", 0.6, "value <= 120", category2)
# subcategory2_2 = RuleNode(["Subcategory2", "Subcategory2.2"], "#0000FF", 0.4, "value <= 140", category2)

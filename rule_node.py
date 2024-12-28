from jsonata import Jsonata


class RuleNode:
    def __init__(self, id_, name, color, weight, rule=None, parent=None):
        self.id = id_
        self.name = name
        self.color = color
        self.weight = weight
        self.children = []
        self.parent = parent
        self.rule = rule

        if parent:
            parent.children.append(self)

    def compile_rule(self):
        if self.rule is None:
            return None
        try:
            return Jsonata(self.rule)
        except Exception as e:
            print(f"Error compiling rule {self.rule}: {e}")
            return None

    def depth_first_search(self, callback):
        callback(self)
        for child in self.children:
            child.depth_first_search(callback)

    @staticmethod
    def classify_data(data, root):
        result = []
        for item in data:
            deepest_matching_node = None
            def match_rule(node):
                expression = node.compile_rule()
                if expression is None:
                    return False
                try:
                    return bool(expression.evaluate(item))
                except Exception as e:
                    print(f"Error evaluating rule {node.rule}: {e}")
                    return False

            def dfs(node):
                nonlocal deepest_matching_node
                if match_rule(node):
                    deepest_matching_node = node
                for child in node.children:
                    dfs(child)

            dfs(root)

            if deepest_matching_node:
                item["category"] = deepest_matching_node.name
                item["color"] = deepest_matching_node.color
                item["weight"] = deepest_matching_node.weight
            else:
                item["category"] = ["uncategorized"]
                item["color"] = "#808080"
                item["weight"] = 0
            result.append(item)
        return result

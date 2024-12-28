from jsonata import Jsonata
from typing import List, Optional, Any


class RuleNode:
    def __init__(self, id_: int, name: List[str], color: str, weight: float, rule: Optional[str] = None,
                 parent: Optional['RuleNode'] = None):
        self.id: int = id_
        self.name: List[str] = name
        self.color: str = color
        self.weight: float = weight
        self.children: List['RuleNode'] = []
        self.parent: Optional['RuleNode'] = parent
        self.rule: Optional[str] = rule

        if parent:
            parent.children.append(self)

    def compile_rule(self) -> Optional[Any]:
        if self.rule is None:
            return None
        try:
            return Jsonata(self.rule)
        except Exception as e:
            print(f"Error compiling rule {self.rule}: {e}")
            return None

    def flatten(self) -> List['RuleNode']:
        flattened = []

        def dfs(node: 'RuleNode') -> None:
            flattened.append(node)
            for child in node.children:
                dfs(child)

        dfs(self)
        return flattened

    def depth_first_search(self, callback) -> None:
        callback(self)
        for child in self.children:
            child.depth_first_search(callback)

    @staticmethod
    def classify_data(data: List[dict], root: 'RuleNode') -> List[dict]:
        result: List[dict] = []
        for item in data:
            deepest_matching_rule: Optional['RuleNode'] = None

            def match_rule(node: 'RuleNode') -> bool:
                expression = node.compile_rule()
                if expression is None:
                    return False
                try:
                    return bool(expression.evaluate(item))
                except Exception as e:
                    print(f"Error evaluating rule {node.rule}: {e}")
                    return False

            def dfs(node: 'RuleNode') -> None:
                nonlocal deepest_matching_rule
                if match_rule(node):
                    deepest_matching_rule = node
                for child in node.children:
                    dfs(child)

            dfs(root)

            if deepest_matching_rule:
                item["category"] = deepest_matching_rule
            else:
                item["category"] = root
            result.append(item)
        return result

    @staticmethod
    def build_sunburst_data(data: List[dict], root: 'RuleNode') -> dict:

        def add_duration(leaf_node: 'RuleNode', duration):
            rule_durations[leaf_node.id] += duration
            if leaf_node.parent:
                add_duration(leaf_node.parent, duration)

        rule_durations = {rule.id: 0 for rule in root.flatten()}
        for item in data:
            add_duration(item['category'], item['endtime'] - item['starttime'])

        def build_node_data(index: int, node: 'RuleNode') -> dict:
            children = []
            for child in node.children:
                children.append(build_node_data(index + 1, child))
            return {
                "name": ".".join(node.name),
                "value": rule_durations[node.id],
                "itemStyle": {"color": node.color},
                "children": children
            }

        graph_root = build_node_data(0, root)
        sum_duration = sum([c['value'] for c in graph_root['children']])
        uncategorized_duration = graph_root['value'] - sum_duration

        graph_root['children'].append({
            "name": "uncategorized",
            "value": uncategorized_duration,
            "itemStyle": {"color": root.color},
            "children": []
        })
        return graph_root

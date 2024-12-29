import itertools
from functools import cached_property

from jsonata import Jsonata
from typing import List, Optional, Any


class RuleNode:
    id_iter = itertools.count()

    def __init__(self, name: List[str], color: str, weight: float,
                 parent: Optional['RuleNode'] = None, rule: Optional[str] = None):
        self.id: int = next(self.id_iter)
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

    @cached_property
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
    def classify_data(data: List[dict], root: 'RuleNode') -> List[int]:
        classified_data = [0 for i in data]
        # sorted by rule depth
        rule_list = sorted(root.flatten, key=lambda x: len(x.name))
        for rule in rule_list:
            expression = rule.compile_rule()
            if expression is None:
                continue
            items = expression.evaluate(data)
            try:
                assert len(items) == len(data)
                # 这个地方应该由用户负责语句的正确性
                for item in items:
                    assert isinstance(item, bool)
            except Exception as e:
                print(f"Error evaluating rule {rule.rule}: {e}")
                continue
            for i, item in enumerate(items):
                if item:
                    classified_data[i] = rule.id
        return classified_data

    @staticmethod
    def build_sunburst_data(data: List[dict], classified_data: List[int], root: 'RuleNode') -> dict:

        def add_duration(leaf_node: 'RuleNode', duration):
            rule_durations[leaf_node.id] += duration
            if leaf_node.parent:
                add_duration(leaf_node.parent, duration)

        rule_lists = {rule.id: rule for rule in root.flatten}
        rule_durations = {rule.id: 0 for rule in rule_lists.values()}
        for item, category_id in zip(data, classified_data):
            add_duration(rule_lists[category_id], item['endtime'] - item['starttime'])

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
        return graph_root['children']

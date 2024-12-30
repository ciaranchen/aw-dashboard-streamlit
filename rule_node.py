import itertools
from functools import cached_property

from jsonata import Jsonata
from typing import List, Optional, Any

from utils import convert_seconds_to_hhmmss


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

    @property
    def extend_name(self):
        return '.'.join(self.name)

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


class ClassifyMethod:
    def __init__(self):
        self.root = RuleNode([], "#000000", 1)
        category1 = RuleNode(["Category1"], "#FF0000", 0.5, self.root, '$.($contains(hostname, "PC"))')
        category2 = RuleNode(["Category2"], "#00FF00", 0.5, self.root, '$.($contains(hostname, "TB"))')
        category3 = RuleNode(["Category3"], "#0000FF", 0.5, self.root, '$.($contains(hostname, "Dell"))')

        RuleNode(["Category1", "Web"], "#FFA500", 0.3, category1,
                 '$.($contains(hostname, "PC") and type="web.tab.current")')
        RuleNode(["Category1", "Window"], "#FFFF00", 0.2, category1,
                 '$.($contains(hostname, "PC") and type="currentwindow")')

    def rules(self):
        return self.root.flatten

    def classify_data(self, data: List[dict]) -> List[int]:
        classified_data = [0 for i in data]
        # sorted by rule depth
        rule_list = sorted(self.root.flatten, key=lambda x: len(x.name))
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

    def build_sunburst_data(self, data: List[dict], classified_data: List[int]) -> dict:

        def add_duration(leaf_node: 'RuleNode', duration):
            rule_durations[leaf_node.id] += duration
            if leaf_node.parent:
                add_duration(leaf_node.parent, duration)

        rule_lists = {rule.id: rule for rule in self.root.flatten}
        rule_durations = {rule.id: 0 for rule in rule_lists.values()}
        for item, category_id in zip(data, classified_data):
            # 转换为秒
            durations = (item['endtime'] - item['starttime']) / 1000000000
            add_duration(rule_lists[category_id], durations)

        names = []
        parents = []
        durations = []
        for rid in rule_lists.keys():
            if rid == 0:
                continue
            rule = rule_lists[rid]
            names.append(rule.extend_name)
            if rule.parent == self.root:
                parents.append("")
            else:
                parents.append(rule.parent.extend_name)
            durations.append(rule_durations[rid])

        duration_strs = [convert_seconds_to_hhmmss(d) for d in durations]

        return {
            "names": names,
            "parents": parents,
            "durations": durations,
            "duration_s": duration_strs
        }

import itertools
import json
from functools import cached_property

from jsonata import Jsonata
from typing import List, Optional, Any

from utils import convert_seconds_to_hhmmss


class RuleNode:
    id_iter = itertools.count()
    default_color = "#CCCCCC"
    # weight 为效率分数
    default_score = 0

    def __init__(self, name: str,
                 color: Optional[str] = None, score: Optional[float] = None,
                 parent: Optional['RuleNode'] = None, rule: Optional[str] = None):
        self.id: int = next(self.id_iter)
        self.name = name
        self.children = []
        self.parent = parent
        if color is None:
            if self.parent:
                self.color = self.parent.color
            else:
                self.color = self.default_color
        else:
            self.color = color
        if score is None:
            if self.parent:
                self.score = self.parent.score
            else:
                self.score = self.default_score
        else:
            self.score = score
        self.rule = rule

    @cached_property
    def names(self):
        res = [self.name]
        node = self.parent
        while node is not None:
            res.append(node.name)
            node = node.parent
        return reversed(res[:-1])

    @cached_property
    def extend_name(self):
        return '.'.join(self.names)

    @property
    def expression(self) -> Optional[Any]:
        if self.rule is None:
            return None
        try:
            return Jsonata(self.rule)
        except Exception as e:
            print(f"Error compiling rule {self.rule}: {e}")
            return None

    @cached_property
    def flatten(self) -> List['RuleNode']:
        flattened = [self]
        for c in self.children:
            flattened.extend(c.flatten)
        return flattened

    @classmethod
    def load_from_json(cls, json_file_path: str):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        return cls._build_rule_node(json_data, None)

    @classmethod
    def _build_rule_node(cls, node_data: dict, parent: Optional['RuleNode']) -> 'RuleNode':
        name = node_data.get('name', '')
        color = node_data.get('color', None)
        weight = node_data.get('weight', None)
        rule = node_data.get('rule', None)
        # 创建 RuleNode 对象
        node = cls(name, color, weight, parent, rule)
        children = node_data.get('children', [])
        for child_data in children:
            # 递归创建子节点
            child = cls._build_rule_node(child_data, node)
            node.children.append(child)
        return node


class ClassifyMethod:
    def __init__(self):
        self.root = RuleNode.load_from_json('rules.json')

    def rules(self):
        return self.root.flatten

    def classify_data(self, data: List[dict]) -> List[int]:
        classified_data = [0 for i in data]
        # sorted by rule depth
        rule_list = self.root.flatten
        for rule in rule_list:
            expression = rule.expression
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
            if rid == self.root.id:
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

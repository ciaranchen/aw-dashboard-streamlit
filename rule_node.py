import itertools
import json
from functools import cached_property

from typing import List, Optional, Any

from rules import Rules


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
    def __init__(self, filename):
        self.root = RuleNode.load_from_json(filename)
        self.rules = Rules

    def classify_data(self, events_data):
        events_data['category'] = self.root.id

        for rule in reversed(self.root.flatten):
            function_name = rule.rule if rule.rule else ''
            function = getattr(self.rules, function_name, None)
            if function:
                filter_data = function(events_data)
                events_data.loc[(events_data['category'] < rule.id) & filter_data, 'category'] = rule.id

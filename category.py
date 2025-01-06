import itertools
import json
from functools import cached_property

from typing import List, Optional

import pandas as pd
import streamlit
import yaml

from rules import Rules


class Category:
    id_iter = itertools.count()
    default_color = "#CCCCCC"
    # weight 为效率分数
    default_score = 0
    rules_bundle = Rules

    def __init__(self, name: str,
                 color: Optional[str] = None, score: Optional[float] = None,
                 parent: Optional['Category'] = None, rule: Optional[str] = None):
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
    def flatten(self) -> List['Category']:
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
    @streamlit.cache_data
    def load_from_yaml(cls, yaml_file_path: str):
        with open(yaml_file_path, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
        return cls._build_rule_node(yaml_data, None)

    @classmethod
    def _build_rule_node(cls, node_data: dict, parent: Optional['Category']) -> 'Category':
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

    @classmethod
    def categorize_data(cls, root: 'Category', events_data):
        events_data['category'] = root.id

        for rule in reversed(root.flatten):
            if rule is root:
                continue
            function_name = rule.rule if rule.rule else ''
            function = getattr(cls.rules_bundle, function_name, None)
            if function:
                filter_data = function(events_data)
                events_data.loc[(events_data['category'] == root.id) & filter_data, 'category'] = rule.id
        for rule in root.flatten:
            events_data.loc[events_data['category'] == rule.id, 'category_name'] = rule.extend_name
            events_data.loc[events_data['category'] == rule.id, 'category_color'] = rule.color
            events_data.loc[events_data['category'] == rule.id, 'category_score'] = rule.score

        # 新增一列，其值为 name 列的截断
        title_prefix_len = 11  # len('aw-watcher-')
        title_truncated_len = 15

        def truncate_title(title):
            title = title[title_prefix_len:]
            if len(title) > title_truncated_len:
                return title[:title_truncated_len] + '...'
            else:
                return title

        events_data['bucket_name'] = events_data['name'].apply(truncate_title)

    @classmethod
    def calc_category_duration(cls, root: 'Category', events_data):
        data_by_category = events_data.groupby('category')
        duration_by_category = data_by_category['duration'].sum().to_frame()

        rule_lists = {rule.id: rule for rule in root.flatten}
        duration_by_category = duration_by_category.reindex(rule_lists.keys(), fill_value=pd.Timedelta(0))

        def add_duration(leaf_node: Category, duration: pd.Timedelta):
            duration_by_category.loc[leaf_node.id] += duration
            if leaf_node.parent:
                add_duration(leaf_node.parent, duration)

        for category, duration in duration_by_category.iterrows():
            add_duration(rule_lists[category], duration)

        duration_by_category['category'] = duration_by_category.index
        for rule in rule_lists.values():
            duration_by_category.loc[duration_by_category['category'] == rule.id, 'category_name'] = rule.extend_name
            duration_by_category.loc[duration_by_category['category'] == rule.id, 'category_color'] = rule.color
            duration_by_category.loc[duration_by_category['category'] == rule.id, 'category_score'] = rule.score
        return duration_by_category

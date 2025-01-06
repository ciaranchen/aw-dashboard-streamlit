# aw-dashboard

A dashboard for ActivityWatch with better custom categories and rules.

To Install:

```shell
pip install -r requirements.txt
```

To Run:

```shell
streamlit run dashboard.py
```

## Config

1. Change Database Location:

   Change database location in `databse.py`. Please refer
   to [this document](https://docs.activitywatch.net/en/latest/directories.html#data) for ActivityWatch data location.

   在 `databse.py` 中修改数据库路径。请参阅[此文档](https://docs.activitywatch.net/en/latest/directories.html#data)了解
   ActivityWatch 数据存储位置。

2. Write your own category:

   1. Write your own classification rules according to the format in `categories.yaml`, specify the category name, category color, and efficiency score. Through the rule field, you can specify the rule function in `rules.py`.
   2. Write your own rule function according to the method in `rules.py`, and its second parameter is Pandas.DataFrame, which is required to return a Pandas.Series for filtering data.

   > Note: Category rules are similar to those in ActivityWatch: deeper categories are prioritized.

   ---

   1. 参照 `categories.yaml`
      中的格式编写自己的分类规则，指定分类的名称、分类的颜色、效率分数。通过rule字段，可指定`rules.py`中的规则函数。
   2. 参照`rules.py`中的方式编写自己的规则函数，其第二个参数为Pandas.DataFrame，要求返回一个Pandas.Series用于筛选数据。

   > Note: 分类规则与 ActivityWatch 中的规则相似：都是优先匹配更深的分类。

## Motivation

Activity Watch是一个非常优秀的软件，但是它的分类规则比较单一。首先它无法对来自Web浏览器的事件进行分类，其次它只能基于json数据的字符串进行正则表达式的匹配，这导致了它的分类规则难以匹配很多情况；即便使用它提供的Category Builder，也有很大一部分事件无法被正确分类。更不必说在同步的情况下，它没法将多个客户端的分类内容进行合并。

我的事件数据不算太多，并且这种统计不需要频繁查看，没有很高的性能要求；但是我有三台电脑，交替地使用Firefox和Chrome。所以我决定自己编写一个分类的机制，并且基于Streamlit给出一个类似Activity的页面。

TODO: 分类的规则应该是可配置的，可以分享的；我认为更好的方式是把分类规则写为一个jsonata之类的允许用户操作数据的DSL，但是在streamlit中操作jsonata可能会比较麻烦，最后还是粗暴地用pandas的方式实现了，这其实是可惜的。
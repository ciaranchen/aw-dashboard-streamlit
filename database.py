import sqlite3
import pandas as pd
import streamlit


class ActivityWatchDataBase:
    def __init__(self):
        # 连接到 SQLite 数据库
        self.conn = sqlite3.connect(r'C:\Users\ciaran\AppData\Local\activitywatch\aw-server-rust\sqlite.db')

    @streamlit.cache_data
    def fetch_bucket_data(_self):
        data = pd.read_sql_query("SELECT * FROM buckets", _self.conn)
        return data

    @streamlit.cache_data
    def fetch_events_data(_self, starttime=None, endtime=None, limit=None, bucket_ids=None):
        query = "SELECT * FROM view_events"
        params = []
        if starttime and endtime:
            query += " WHERE starttime >=? AND endtime <=?"
            params.extend([starttime, endtime])
        elif starttime:
            query += " WHERE starttime >=?"
            params.append(starttime)
        elif endtime:
            query += " WHERE endtime <=?"
            params.append(endtime)
        if bucket_ids:
            if len(query) == len("SELECT * FROM view_events"):
                query += " WHERE"
            else:
                query += " AND"
            query += f" bucketrow IN ({','.join('?' * len(bucket_ids))})"
            params.extend(bucket_ids)
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        data = pd.read_sql_query(query, _self.conn, params=params)
        return data


if __name__ == "__main__":
    # 示例使用
    import json

    db = ActivityWatchDataBase()
    data = db.fetch_events_data(
        starttime=1732996800000000000,
        endtime=1735156800000000000,
        limit=20,
        bucket_ids=[2, 3, 4])
    # print(data)

    from category import Category

    root = Category.load_from_yaml('categories.yaml')
    Category.categorize_data(root, data)

    # 按 category 分组并计算 duration 的总和
    timezone = 'Asia/Shanghai'
    data['start_datetime'] = (pd.to_datetime(data['starttime'], unit='ns', utc=True)
                              .dt.tz_convert(timezone))
    data['end_datetime'] = (pd.to_datetime(data['endtime'], unit='ns', utc=True)
                            .dt.tz_convert(timezone))
    # 计算 duration
    data['duration'] = data['end_datetime'] - data['start_datetime']
    duration_by_category = data.groupby('category')['duration'].sum()
    print(duration_by_category)

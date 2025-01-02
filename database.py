import sqlite3
import pandas as pd


class ActivityWatchDataBase:
    def __init__(self):
        # 连接到 SQLite 数据库
        self.conn = sqlite3.connect(r'C:\Users\ciaran\AppData\Local\activitywatch\aw-server-rust\sqlite.db')

    def __del__(self):
        self.conn.close()

    def fetch_bucket_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM buckets")
        rows = cursor.fetchall()
        # result = [dict(row) for row in rows]
        return rows

    def fetch_events_data(self, starttime=None, endtime=None, limit=None, bucket_ids=None):
        cursor = self.conn.cursor()
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
        data = pd.read_sql_query(query, self.conn, params=params)
        return data


if __name__ == "__main__":
    # 示例使用
    import json

    db = ActivityWatchDataBase()
    data = db.fetch_events_data(
        starttime=1732996800000000000,
        endtime=1735156800000000000,
        bucket_ids=[2, 3, 4])
    data['start_datetime'] = pd.to_datetime(data['starttime'], unit='ns', utc=True).dt.tz_convert('Asia/Shanghai')
    data['end_datetime'] = pd.to_datetime(data['endtime'], unit='ns', utc=True).dt.tz_convert('Asia/Shanghai')
    print(data)

    from rule_node import ClassifyMethod
    from rules_python import Rules

    cm = ClassifyMethod()
    r = Rules()
    data['category'] = cm.root.id

    for rule in reversed(cm.root.flatten):
        function_name = rule.rule if rule.rule else ''
        function = getattr(r, function_name, None)
        if function:
            filter_data = function(data)
            data.loc[(data['category'] < rule.id) & filter_data, 'category'] = rule.id


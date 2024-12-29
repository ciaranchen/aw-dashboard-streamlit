import sqlite3


class ActivityWatchDataBase:
    def __init__(self):
        # 连接到 SQLite 数据库
        self.conn = sqlite3.connect(r'C:\Users\ciaran\AppData\Local\activitywatch\aw-server-rust\sqlite.db')
        # 设置连接的行工厂为 sqlite3.Row
        # 这样查询结果将以字典形式返回
        self.conn.row_factory = sqlite3.Row

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
            query += " LIMIT?"
            params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(dict(row))
        return result


if __name__ == "__main__":
    # 示例使用
    import json

    db = ActivityWatchDataBase()
    data = db.fetch_events_data(
        starttime=1732996800000000000,
        endtime=1735156800000000000,
        limit=20, bucket_ids=[1, 3, 4])
    print(json.dumps(data))

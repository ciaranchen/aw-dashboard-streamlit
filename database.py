import sqlite3


def get_db_connection():
    # 连接到 SQLite 数据库
    conn = sqlite3.connect(r'C:\Users\ciaran\AppData\Local\activitywatch\aw-server-rust\sqlite.db')
    # 设置连接的行工厂为 sqlite3.Row
    # 这样查询结果将以字典形式返回
    conn.row_factory = sqlite3.Row
    return conn


def fetch_data(starttime=None, endtime=None, limit=None):
    conn = get_db_connection()
    cursor = conn.cursor()
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
    if limit:
        query += " LIMIT?"
        params.append(limit)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append(dict(row))
    return result


if __name__ == "__main__":
    # 示例使用
    data = fetch_data()
    print(data)

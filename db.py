import psycopg2
from psycopg2.extras import RealDictCursor

class Database:
    def __init__(self, dsn):
        self.dsn = dsn

    def connect(self):
        return psycopg2.connect(self.dsn)

    def fetch_all(self, query, params=None):
        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                return cur.fetchall()

    def execute(self, query, params=None):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                conn.commit()

import psycopg2
from psycopg2.extras import RealDictCursor

class Database:
    def __init__(self, dsn):
        self.dsn = dsn

    def connect(self):
        return psycopg2.connect(self.dsn)

    def fetch_all(self, query, params=None):
        with self.connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                return cur.fetchall()

    def execute(self, query, params=None):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                conn.commit()

    def execute_returning(self, query, params=None):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                result = cur.fetchone()
                conn.commit()
                return result

    def call_function(self, func_name, params=None):
        placeholders = ','.join(['%s'] * (len(params) if params else 0))
        sql = f"SELECT * FROM {func_name}({placeholders});"
        return self.fetch_all(sql, params)



    def call_function(self, func_name, params=None):
        placeholders = ','.join(['%s'] * (len(params) if params else 0))
        sql = f"SELECT * FROM {func_name}({placeholders});"
        return self.fetch_all(sql, params)
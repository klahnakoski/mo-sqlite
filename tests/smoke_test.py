from mo_sqlite import Sqlite, sql_query

db = Sqlite()
with db.transaction() as t:
    t.execute("CREATE TABLE IF NOT EXISTS test (a INTEGER, b TEXT)")
    t.execute("INSERT INTO test VALUES (1, 'one')")
tables = db.get_tables()
db.stop()
print(tables)

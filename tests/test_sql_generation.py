from unittest import TestCase

from mo_sqlite import sql_delete


class TestSqlGeneration(TestCase):
    def test_delete(self):
        sql = str(sql_delete("$$", {"eq": {"a": 1}}))
        self.assertEqual(remove_extra_space(sql), 'DELETE FROM "$$" WHERE a = 1')

    def test_delete_no_where(self):
        sql = str(sql_delete("$$"))
        self.assertEqual(remove_extra_space(sql), 'DELETE FROM "$$" WHERE 1')

    def test_delete_using_in(self):
        sql = str(sql_delete("$$", {"in": {"a": [1, 2]}}))
        self.assertEqual(remove_extra_space(sql), 'DELETE FROM "$$" WHERE a IN ( 1, 2 )')


def remove_extra_space(sql):
    sql = sql.replace("\n", " ").strip()
    while "  " in sql:
        sql = sql.replace("  ", " ")
    return sql
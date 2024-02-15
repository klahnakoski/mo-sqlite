# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from unittest import TestCase

from mo_files import File

from mo_sqlite import Sqlite


class TestDatabase(TestCase):
    def test_change_only(self):
        file = File("tests/database.sqlite")
        file.delete()

        db = Sqlite(file)

        with db.transaction() as t:
            t.execute("CREATE TABLE t (a INTEGER, b INTEGER)")

        with db.transaction() as t:
            t.execute("INSERT INTO t (a, b) VALUES (1, 2)")

        with db.transaction() as t:
            result = t.query("SELECT * FROM t")

        self.assertEqual(result.data, [(1, 2)])

# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from unittest import TestCase

from mo_sql import sql_iso

from mo_dots import Data
from mo_threads import Signal, Thread

import mo_sqlite
from mo_sqlite import Sqlite, quote_value
from mo_sqlite.database import DOUBLE_TRANSACTION_ERROR

mo_sqlite.DEBUG = True


class TestTransaction(TestCase):
    def test_interleaved_transactions(self):
        db, threads, signals = self._setup()
        a, b = signals.a, signals.b

        # INTERLEAVED TRANSACTION STEPS
        for i in range(3):
            self._perform(a, i)
            self._perform(b, i)

        self._teardown(db, threads)

    def test_transactionqueries(self):
        db = Sqlite()
        db.query("CREATE TABLE my_table (value TEXT)")

        with db.transaction() as t:
            t.execute("INSERT INTO my_table (value) VALUES ('a')")
            try:
                result1 = db.query("SELECT * FROM my_table")
                assert False
            except Exception as e:
                assert DOUBLE_TRANSACTION_ERROR in e
            result2 = t.query("SELECT * FROM my_table")

        assert result2.data[0][0] == "a"

    def test_two_commands(self):
        db, threads, signals = self._setup()
        a, b = signals.a, signals.b

        self._perform(a, 0)
        self._perform(a, 1)
        self._perform(b, 0)
        self._perform(b, 1)
        self._perform(a, 2)
        self._perform(b, 2)

        self._teardown(db, threads)

    def test_nested_transaction1(self):
        db = Sqlite()
        db.query("CREATE TABLE my_table (value TEXT)")

        with db.transaction() as t:
            t.execute("INSERT INTO my_table VALUES ('a')")

            result = t.query("SELECT * FROM my_table")
            assert len(result.data) == 1
            assert result.data[0][0] == "a"

            with db.transaction() as t2:
                t2.execute("INSERT INTO my_table VALUES ('b')")

        self._teardown(db, {})

    def test_nested_transaction2(self):
        db = Sqlite()
        db.query("CREATE TABLE my_table (value TEXT)")

        with db.transaction() as t:
            with db.transaction() as t2:
                t2.execute("INSERT INTO my_table VALUES ('b')")

                result = t2.query("SELECT * FROM my_table")
                assert len(result.data) == 1
                assert result.data[0][0] == "b"

            t.execute("INSERT INTO my_table VALUES ('a')")

        self._teardown(db, {})

    def _work(self, name, db, sigs, please_stop):
        try:
            sigs[0].begin.wait()
            with db.transaction() as t:
                sigs[0].done.go()
                sigs[1].begin.wait()
                t.execute("INSERT INTO my_table VALUES " + sql_iso(quote_value(name)))
                sigs[1].done.go()

                sigs[2].begin.wait()
                result = t.query("SELECT * FROM my_table WHERE value=" + quote_value(name))
                assert len(result.data) == 1
                assert result.data[0][0] == name
            sigs[2].done.go()
        finally:
            # RELEASE ALL SIGNALS, THIS IS ENDING BADLY
            for s in sigs:
                s.done.go()

    def _setup(self):
        threads = Data()
        signals = Data()

        db = Sqlite()
        db.query("CREATE TABLE my_table (value TEXT)")

        for name in ["a", "b"]:
            signals[name] = [{"begin": Signal(), "done": Signal()} for _ in range(4)]
            threads[name] = Thread.run(name, self._work, name, db, signals[name])

        return db, threads, signals

    def _teardown(self, db, threads):
        for t in threads.values():
            t.join()
            t.join()

        result = db.query("SELECT * FROM my_table ORDER BY value")
        assert len(result.data) == 2
        assert result.data[0][0] == "a"
        assert result.data[1][0] == "b"

    def _perform(self, c, i):
        c[i].begin.go()
        c[i].done.wait()

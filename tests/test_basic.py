# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
import re
from unittest import TestCase

from mo_sql import sql_list
from mo_sqlite import Sqlite, quote_column, ConcatSQL, SQL_SELECT, SQL_FROM
from mo_sqlite.sql_script import SqlStep, SelectOne, SqlTree

whitespace = re.compile(r"\s+", re.MULTILINE)


class TestBasic(TestCase):


    def test_one_nested_query(self):
        # FILL DATABASE WITH TWO TABLES, ONE WITH A FOREIGN KEY TO THE OTHER
        db = Sqlite()
        with db.transaction() as t:
            # create table of some people
            t.execute("CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT)")
            t.execute("INSERT INTO people (name) VALUES ('kyle')")
            t.execute("INSERT INTO people (name) VALUES ('joe')")
            t.execute("INSERT INTO people (name) VALUES ('jane')")
            # create table of some pets, with foreign key to people
            t.execute(
                "CREATE TABLE pets (id INTEGER PRIMARY KEY, name TEXT, _order INTEGER, owner INTEGER REFERENCES"
                " people(id))"
            )
            t.execute("INSERT INTO pets (name, _order, owner) VALUES ('fido', 0, 1)")
            t.execute("INSERT INTO pets (name, _order, owner) VALUES ('spot', 1, 1)")
            t.execute("INSERT INTO pets (name, _order, owner) VALUES ('fluffy', 0, 2)")

        people = SqlStep(
            None,
            ConcatSQL(
                SQL_SELECT, sql_list([quote_column("id"), quote_column("name")]), SQL_FROM, quote_column("people")
            ),
            [SelectOne("name", quote_column("name"))],
            id=(quote_column("id"),),
            order=(),
        )
        pets = SqlStep(
            people,
            ConcatSQL(
                SQL_SELECT,
                sql_list([quote_column("id"), quote_column("name"), quote_column("_order"), quote_column("owner")]),
                SQL_FROM,
                quote_column("pets"),
            ),
            [SelectOne("pets.$A.name", quote_column("name"))],
            id=(quote_column("owner"), quote_column("id")),
            order=(quote_column("_order"),),
        )

        sql = SqlTree([pets]).to_sql()
        self.assertEqual(whitespace.sub("", str(sql)), """SELECTi0_0,c0_0,NULLASo1_0,NULLASi1_0,NULLASi1_1,NULLASc1_0FROM(SELECTidASi0_0,nameASc0_0FROM(SELECTid,nameFROMpeople))ASt0UNIONALLSELECTi0_0,NULLASc0_0,o1_0,i1_0,i1_1,c1_0FROM(SELECTidASi0_0FROM(SELECTid,nameFROMpeople))ASt0LEFTJOIN(SELECT_orderASo1_0,ownerASi1_0,idASi1_1,nameASc1_0FROM(SELECTid,name,_order,ownerFROMpets))ASt1ONi1_0=i0_0ORDERBYo0_0ISNOTNULL,o0_0,o1_0ISNOTNULL,o1_0,o1_1ISNOTNULL,o1_1,o1_2ISNOTNULL,o1_2""")

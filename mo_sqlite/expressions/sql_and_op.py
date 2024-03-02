# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http:# mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from jx_base.expressions import SqlAndOp as _SqlAndOp
from mo_sql import NO_SQL, SQL_LP, SQL_RP
from mo_sqlite.utils import SQL_AND, SQL


class SqlAndOp(_SqlAndOp, SQL):
    def __iter__(self):
        op = NO_SQL
        for t in self.terms:
            yield from op
            op = SQL_AND
            yield from SQL_LP
            yield from t
            yield from SQL_RP


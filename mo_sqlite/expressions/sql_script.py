# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http:# mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#

from jx_base.expressions import (
    FALSE,
    SqlScript as _SQLScript,
    TRUE,
    MissingOp,
)
from jx_base.expressions.variable import is_variable
from jx_base.language import is_op, Expression, Language
from mo_json import JxType
from mo_logs import Log
from mo_sql import SQL, SQL_CASE, SQL_END, SQL_NULL, SQL_THEN, SQL_WHEN, ConcatSQL, sql_iso, SQL_NOT

SQLang = Language("SQLang")


class SqlScript(_SQLScript, SQL):
    """
    DESCRIBE AN UNSTRUCTURED SQL SCRIPT
    """

    __slots__ = ("_jx_type", "_expr", "frum", "miss", "schema")

    def __init__(self, jx_type, expr, frum, miss=None, schema=None):
        object.__init__(self)
        if expr == None or expr is self:
            Log.error("expecting expr")
        if not isinstance(expr, SQL):
            Log.error("Expecting SQL")
        if not isinstance(jx_type, JxType):
            Log.error("Expecting JsonType")
        if schema is None:
            Log.error("expecting schema")

        if miss is None:
            self.miss = frum.missing(SQLang)
        else:
            self.miss = miss
        self._jx_type = jx_type
        self._expr = expr
        self.frum = frum  # THE ORIGINAL EXPRESSION THAT MADE expr
        self.schema = schema

    @property
    def name(self):
        return "."

    @property
    def expr(self):
        if isinstance(self._expr, SQL) and isinstance(self._expr, Expression):
            return self._expr
        return self

    def __getitem__(self, item):
        if not self.many:
            if item == 0:
                return self
            else:
                Log.error("this is a primitive value")
        else:
            Log.error("do not know how to handle")

    def __iter__(self):
        """
        ASSUMED TO OVERRIDE SQL.__iter__()
        """
        return self._sql().__iter__()

    @property
    def sql(self):
        return self._sql()

    def _sql(self):
        self.miss = self.miss.partial_eval(SQLang)
        if self.miss is TRUE:
            return SQL_NULL
        elif self.miss is FALSE or is_variable(self.frum):
            return self._expr

        if is_op(self.miss, MissingOp) and is_variable(self.frum) and self.miss.expr == self.frum:
            return self._expr

        return ConcatSQL(SQL_CASE, SQL_WHEN, SQL_NOT, sql_iso(self.miss.to_sql(self.schema)), SQL_THEN, self._expr, SQL_END, )

    def __str__(self):
        return str(self._sql())

    def to_sql(self, schema) -> "SqlScript":
        return self

    def missing(self, lang):
        return self.miss

    def __data__(self):
        return {"script": self.expr}

    def __eq__(self, other):
        if not isinstance(other, _SQLScript):
            return False
        return self.expr == other.expr

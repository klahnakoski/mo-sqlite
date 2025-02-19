# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://www.mozilla.org/en-US/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#


from jx_base.expressions._utils import TRUE
from jx_base.expressions.expression import Expression
from jx_base.expressions.false_op import FALSE
from mo_imports import expect
from mo_json.types import JX_BOOLEAN

NotOp = expect("NotOp")


class ExistsOp(Expression):
    _jx_type = JX_BOOLEAN

    def __init__(self, term):
        Expression.__init__(self, term)
        self.expr = term

    def __data__(self):
        return {"exists": self.expr.__data__()}

    def __call__(self, row, rownum=None, rows=None):
        value = self.expr(row, rownum, rows)
        return value != None and value != ""

    def vars(self):
        return self.expr.vars()

    def map(self, map_):
        return ExistsOp(self.expr.map(map_))

    def missing(self, lang):
        return FALSE

    def invert(self, lang):
        return self.expr.missing(lang)

    def exists(self):
        return TRUE

    def partial_eval(self, lang):
        return (NotOp(self.expr.missing(lang))).partial_eval(lang)

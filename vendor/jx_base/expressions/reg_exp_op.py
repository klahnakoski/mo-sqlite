# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://www.mozilla.org/en-US/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
import re

from jx_base.expressions.expression import Expression
from jx_base.expressions.literal import is_literal
from jx_base.expressions.or_op import OrOp
from jx_base.expressions.variable import is_variable
from jx_base.language import is_op
from mo_json.types import JX_BOOLEAN


class RegExpOp(Expression):
    has_simple_form = True
    _jx_type = JX_BOOLEAN

    def __init__(self, *terms):
        Expression.__init__(self, *terms)
        self.expr, self.pattern = terms

    def __data__(self):
        if is_variable(self.expr) and is_literal(self.pattern):
            return {"regexp": {self.expr.var: self.pattern.value}}

        return {"regexp": [self.expr.__data__(), self.pattern.__data__()]}

    def __eq__(self, other):
        if not is_op(other, RegExpOp):
            return False
        return self.expr == other.expr and self.pattern == other.pattern

    def __call__(self, row, rownum=None, rows=None):
        return bool(re.match(self.pattern(row, rownum, rows), self.expr(row, rownum, rows)))

    def vars(self):
        return self.expr.vars() | self.pattern.vars()

    def map(self, map_):
        return RegExpOp(self.expr.map(map_), self.pattern.map(map_))

    def missing(self, lang):
        return OrOp(self.expr.missing(lang), self.pattern.missing(lang))

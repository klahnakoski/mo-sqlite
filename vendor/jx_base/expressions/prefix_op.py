# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://www.mozilla.org/en-US/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#


from mo_dots import is_data, is_missing

from jx_base.expressions._utils import jx_expression
from jx_base.expressions.strict_starts_with_op import StrictStartsWithOp
from jx_base.expressions.case_op import CaseOp
from jx_base.expressions.expression import Expression
from jx_base.expressions.false_op import FALSE
from jx_base.expressions.is_text_op import IsTextOp
from jx_base.expressions.literal import is_literal, Literal
from jx_base.expressions.null_op import NULL
from jx_base.expressions.true_op import TRUE
from jx_base.expressions.variable import Variable, is_variable
from jx_base.expressions.when_op import WhenOp
from jx_base.language import is_op
from mo_future import first
from mo_json.types import JX_BOOLEAN


class PrefixOp(Expression):
    has_simple_form = True
    _jx_type = JX_BOOLEAN

    def __init__(self, expr, prefix):
        Expression.__init__(self, expr, prefix)
        self.expr = expr
        self.prefix = prefix

    _patterns = [{"prefix": {"expr": "prefix"}}, {"prefix": ["expr", "prefix"]}]

    @classmethod
    def define(cls, expr):
        term = expr.get("prefix")
        if not term:
            return PrefixOp(NULL, NULL)
        elif is_data(term):
            kv_pair = first(term.items())
            if kv_pair:
                expr, const = first(term.items())
                return PrefixOp(Variable(expr), Literal(const))
            else:
                return TRUE
        else:
            expr, const = term
            return PrefixOp(jx_expression(expr), jx_expression(const))

    def __data__(self):
        if self.expr == None:
            return {"prefix": {}}
        elif is_variable(self.expr) and is_literal(self.prefix):
            return {"prefix": {self.expr.var: self.prefix.value}}
        else:
            return {"prefix": [self.expr.__data__(), self.prefix.__data__()]}

    def __call__(self, row, rownum=None, rows=None):
        expr = self.expr(row, rownum, rows)
        if is_missing(expr):
            return None
        prefix = self.prefix(row, rownum, rows)
        if is_missing(prefix):
            return None
        return expr.startswith(prefix)

    def vars(self):
        if self.expr is NULL:
            return set()
        return self.expr.vars() | self.prefix.vars()

    def map(self, map_):
        if self.expr is NULL:
            return self
        else:
            return PrefixOp(self.expr.map(map_), self.prefix.map(map_))

    def missing(self, lang):
        return FALSE

    def partial_eval(self, lang):
        prefix = IsTextOp(self.prefix).partial_eval(lang)
        expr = IsTextOp(self.expr).partial_eval(lang)
        return CaseOp(
            WhenOp(prefix.missing(lang), then=TRUE),
            WhenOp(expr.missing(lang), then=FALSE),
            StrictStartsWithOp(expr, prefix),
        ).partial_eval(lang)

    def __eq__(self, other):
        if not is_op(other, PrefixOp):
            return False
        return self.expr == other.frum and self.prefix == other.prefix

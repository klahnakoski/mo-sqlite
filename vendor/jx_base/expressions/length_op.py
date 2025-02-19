# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://www.mozilla.org/en-US/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from mo_dots import is_missing

from jx_base.expressions.expression import Expression
from jx_base.expressions.literal import Literal
from jx_base.expressions.literal import is_literal
from jx_base.expressions.null_op import NULL
from jx_base.language import is_op
from mo_future import is_text
from mo_json import JX_INTEGER


class LengthOp(Expression):
    _jx_type = JX_INTEGER

    def __init__(self, term):
        Expression.__init__(self, term)
        self.term = term

    def __call__(self, row, rownum=None, rows=None):
        value = self.term(row, rownum, rows)
        if is_missing(value):
            return None
        return len(value)

    def __eq__(self, other):
        if is_op(other, LengthOp):
            return self.term == other.term

    def __data__(self):
        return {"length": self.term.__data__()}

    def vars(self):
        return self.term.vars()

    def map(self, map_):
        return LengthOp(self.term.map(map_))

    def missing(self, lang):
        return self.term.missing(lang)

    def partial_eval(self, lang):
        term = self.term.partial_eval(lang)
        if is_literal(term):
            if is_text(term.value):
                return lang.Literal(len(term.value))
            else:
                return NULL
        else:
            return lang.LengthOp(term)

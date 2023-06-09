# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http:# mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#


from jx_base.expressions.expression import Expression
from jx_base.expressions.false_op import FALSE
from jx_base.expressions.literal import Literal
from jx_base.expressions.literal import is_literal
from jx_base.expressions.null_op import NULL
from jx_base.expressions.null_op import NullOp
from jx_base.language import is_op
from mo_dots import is_many
from mo_json.types import JX_NUMBER
from mo_math import MIN


class MinOp(Expression):
    _data_type = JX_NUMBER

    def __init__(self, *terms, default=NULL):
        Expression.__init__(self, *terms)
        if terms == None:
            self.terms = []
        elif is_many(terms):
            self.terms = terms
        else:
            self.terms = [terms]
        self.default = default

    def __data__(self):
        return {
            "min": [t.__data__() for t in self.terms],
            "default": self.default.__data__(),
        }

    def vars(self):
        output = set()
        for t in self.terms:
            output |= t.vars()
        return output

    def map(self, map_):
        return MinOp(*(t.map(map_) for t in self.terms))

    def missing(self, lang):
        return FALSE

    def partial_eval(self, lang):
        minimum = None
        terms = []
        for t in self.terms:
            simple = t.partial_eval(lang)
            if is_op(simple, NullOp):
                pass
            elif is_literal(simple):
                minimum = MIN(minimum, simple.value)
            else:
                terms.append(simple)
        if len(terms) == 0:
            if minimum == None:
                return NULL
            else:
                return Literal(minimum)
        else:
            if minimum == None:
                output = MinOp(*terms)
            else:
                output = MinOp(Literal(minimum), *terms)

        return output

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
from jx_base.expressions.literal import Literal, is_literal
from jx_base.expressions.null_op import NULL
from mo_dots import is_many
from mo_json.types import JX_NUMBER
from mo_math import MAX


class MaxOp(Expression):
    _data_type = JX_NUMBER

    def __init__(self, *terms, default=NULL):
        Expression.__init__(self, *terms)
        if terms == None:
            self.terms = []
        elif is_many(terms):
            self.terms = [t for t in terms if t != None]
        else:
            self.terms = [terms]
        self.default = default

    def __data__(self):
        return {
            "max": [t.__data__() for t in self.terms],
            "default": self.default.__data__(),
        }

    def vars(self):
        output = set()
        for t in self.terms:
            output |= t.vars()
        return output

    def map(self, map_):
        return MaxOp(*(t.map(map_) for t in self.terms))

    def missing(self, lang):
        return FALSE

    def partial_eval(self, lang):
        maximum = None
        terms = []
        for t in self.terms:
            simple = t.partial_eval(lang)
            if simple is NULL:
                pass
            elif is_literal(simple):
                maximum = MAX([maximum, simple.value])
            else:
                terms.append(simple)
        if len(terms) == 0:
            if maximum is None:
                return NULL
            else:
                return Literal(maximum)
        else:
            if maximum is None:
                output = MaxOp(terms)
            else:
                output = MaxOp([Literal(maximum)] + terms)

        return output

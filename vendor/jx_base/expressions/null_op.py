# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://www.mozilla.org/en-US/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#


from jx_base.expressions.false_op import FALSE
from jx_base.expressions.literal import Literal
from jx_base.expressions.true_op import TRUE
from jx_base.language import TYPE_ORDER
from mo_dots import Null
from mo_imports import export
from mo_json.types import JX_IS_NULL
from mo_logs import Log


class NullOp(Literal):
    """
    FOR USE WHEN EVERYTHING IS EXPECTED TO BE AN Expression
    USE IT TO EXPECT A NULL VALUE IN assertAlmostEqual
    """

    _jx_type = JX_IS_NULL

    @classmethod
    def define(cls, expr):
        return NULL

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls, *args, **kwargs)

    def __init__(self, op=None, term=None):
        Literal.__init__(self, None)

    def __nonzero__(self):
        return True

    def __eq__(self, other):
        return other is NULL

    def __gt__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __ge__(self, other):
        if other == None:
            return True
        return False

    def __le__(self, other):
        if other == None:
            return True
        return False

    def __data__(self):
        return {"null": {}}

    def vars(self):
        return set()

    def map(self, map_):
        return self

    def missing(self, lang):
        return TRUE

    def invert(self, lang):
        return TRUE

    def exists(self):
        return FALSE

    @property
    def jx_type(self):
        return JX_IS_NULL

    def __call__(self, row=None, rownum=None, rows=None):
        return Null

    def __str__(self):
        return "null"

    def __hash__(self):
        return id(None)

    def __bool__(self):
        Log.error("Detecting truthiness of NullOp is too confusing to be allowed")

    def __nonzero__(self):
        Log.error("Detecting truthiness of NullOp is too confusing to be allowed")


NULL = NullOp()
TYPE_ORDER[NullOp] = 9
TYPE_ORDER[NULL] = 9

export("jx_base.expressions._utils", NULL)
export("jx_base.expressions.expression", NULL)
export("jx_base.expressions.strict_in_op", NULL)
export("jx_base.expressions.literal", NULL)
export("jx_base.expressions.base_multi_op", NULL)

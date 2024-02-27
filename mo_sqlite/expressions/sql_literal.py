# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http:# mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from jx_base.expressions import Literal
from mo_future import extend
from mo_sql import SQL
from mo_sqlite.utils import quote_value


SqlLiteral = Literal


if SQL not in Literal.__bases__:
    Literal.__bases__ = Literal.__bases__ + (SQL,)


@extend(Literal)
def __iter__(self):
    yield from quote_value(self.value)


# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http:# mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from dataclasses import dataclass

from jx_base import NULL
from jx_base.expressions import CaseOp as _CaseOp
from mo_sql import (
    SQL,
    SQL_CASE,
    SQL_ELSE,
    SQL_END,
    SQL_THEN,
    SQL_WHEN,
)


@dataclass
class When:
    when: SQL
    then: SQL

    def __iter__(self):
        yield from SQL_WHEN
        yield from self.when
        yield from SQL_THEN
        yield from self.then


class CaseOp(_CaseOp):

    def __init__(self, whens, _else):
        super().__init__(*whens, _else)


    def __iter__(self):
        yield from SQL_CASE
        for w in self.whens:
            yield from w
        if self.els_ is not NULL:
            yield from SQL_ELSE
            yield from self.els_
        yield from SQL_END

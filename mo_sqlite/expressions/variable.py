# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http:# mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from mo_dots import concat_field
from mo_sql import SQL
from jx_base.expressions import Variable as _Variable
from mo_sqlite import quote_column


class Variable(_Variable, SQL):

    __new__ = object.__new__

    def __init__(self, es_index, es_column):
        _Variable.__init__(self, concat_field(es_index, es_column))
        self.es_index = es_index
        self.es_column = es_column

    def __iter__(self):
        yield from quote_column(self.es_index, self.es_column)

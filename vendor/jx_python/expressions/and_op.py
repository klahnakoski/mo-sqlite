# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://www.mozilla.org/en-US/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#


from jx_base.expressions import AndOp as _AndOp, FALSE, PythonScript
from jx_python.expressions.to_boolean_op import ToBooleanOp
from jx_python.utils import merge_locals
from mo_json import JX_BOOLEAN


class AndOp(_AndOp):
    def to_python(self, loop_depth=0):
        if not self.terms:
            return PythonScript({}, loop_depth, JX_BOOLEAN, "True", self, FALSE)

        sources, locals = zip(
            *((c.source, c.locals) for t in self.terms for c in [ToBooleanOp(t).to_python(loop_depth)])
        )
        return PythonScript(
            merge_locals(*locals), loop_depth, JX_BOOLEAN, " and ".join(f"({s})" for s in sources), self, FALSE,
        )

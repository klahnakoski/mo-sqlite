from mo_sqlite.expressions.select_op import SelectOp
from mo_sqlite.expressions.sql_eq_op import SqlEqOp
from mo_sqlite.expressions.select_op import SelectOp
from mo_sqlite.expressions.variable import Variable

from mo_sqlite.expressions._utils import Sqlite

Sqlite.register_ops(vars())

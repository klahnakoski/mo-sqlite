# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from dataclasses import dataclass
from typing import List, Tuple, Set

from jx_base.expressions import Expression
from mo_collections.queue import Queue
from mo_sql import (
    JoinSQL,
    ConcatSQL,
    SQL_UNION_ALL,
    SQL_ORDERBY,
    SQL_LEFT_JOIN,
    sql_iso,
    SQL_EQ,
    SQL_AND,
    SQL_ON,
    SQL_SELECT,
    SQL_FROM,
    SQL_COMMA,
    SQL,
    SQL_NULL,
    sql_list,
    SQL_IS_NOT_NULL,
)
from mo_sqlite import sql_alias, quote_column


@dataclass
class SelectOne:
    name: str
    value: Expression


class SqlStep:
    def __init__(self, parent, sql, selects, id, order):
        self.parent: SqlStep = parent
        self.id = -1
        self.start = None  # WHERE TO PLACE THE COLUMNS IN THE SELECT
        self.end = None  # THE END OF THE COLUMNS IN THE SELECT
        self.sql: SQL = sql  # ASSUMED TO BE A SUB QUERY, INCLUDING THE id AND order COLUMNS
        self.selects: List[SelectOne] = selects
        self.uids: Tuple[Expression] = id  # TECHNICALLY EXPRESSIONS, LIKELY JUST COLUMN NAMES
        self.order: Tuple[Expression] = order

    def position(self, done, all_selects):
        if self in done:
            return

        if self.parent:
            self.parent.position(done, all_selects)
        self.id = len(done)
        done.append(self)
        self.start = len(all_selects)
        for oi, _ in enumerate(self.order):
            all_selects.append(f"o{self.id}_{oi}")
        for ii, _ in enumerate(self.uids):
            all_selects.append(f"i{self.id}_{ii}")
        for ci, _ in enumerate(self.selects):
            all_selects.append(f"c{self.id}_{ci}")
        self.end = len(all_selects)

    def node_sql(self, all_selects):
        """
        SQL TO PULL MINIMUM COLUMNS FOR LEFT JOINS
        """
        columns = [
            *(sql_alias(ov, f"o{self.id}_{oi}") for oi, ov in enumerate(self.order)),
            *(sql_alias(iv, f"i{self.id}_{ii}") for ii, iv, in enumerate(self.uids)),
        ]
        parent_end = self.parent.end if self.parent else 0
        start_of_values = self.start + len(self.order) + len(self.uids)
        return (
            [
                *(sql_alias(SQL_NULL, s) for s in all_selects[parent_end : self.start]),
                *(quote_column(s) for s in all_selects[self.start : start_of_values]),
                *(sql_alias(SQL_NULL, s) for s in all_selects[start_of_values : self.end]),
            ],
            sql_alias(sql_iso(ConcatSQL(SQL_SELECT, sql_list(columns), SQL_FROM, sql_iso(self.sql),)), f"t{self.id}",),
        )

    def leaf_sql(self, all_selects):
        """
        SQL TO PULL ALL COLUMNS FOR LEAF
        """
        columns = [
            *(sql_alias(ov, f"o{self.id}_{oi}") for oi, ov in enumerate(self.order)),
            *(sql_alias(iv, f"i{self.id}_{ii}") for ii, iv, in enumerate(self.uids)),
            *(sql_alias(cv.value, f"c{self.id}_{ci}") for ci, cv in enumerate(self.selects)),
        ]
        parent_end = self.parent.end if self.parent else 0
        return (
            [
                *(sql_alias(SQL_NULL, s) for s in all_selects[parent_end : self.start]),
                *(quote_column(s) for s in all_selects[self.start : self.end]),
                *(sql_alias(SQL_NULL, s) for s in all_selects[self.end :]),
            ],
            sql_alias(sql_iso(ConcatSQL(SQL_SELECT, sql_list(columns), SQL_FROM, sql_iso(self.sql),)), f"t{self.id}",),
        )

    def branch_sql(self, done: List, sql_queries: List[SQL], all_selects: List[str]) -> Tuple:
        """
        return tuple of SqlSteps for caller to make into a SqlScript
        insert branch query into sql_queries
        """
        if self in done:
            return

        if not self.parent:
            done.append(self)
            selects, leaf = self.leaf_sql(all_selects)
            sql_queries.append(ConcatSQL(SQL_SELECT, JoinSQL(SQL_COMMA, selects), SQL_FROM, leaf))
            return (self,)

        nested_path = self.parent.branch_sql(done, sql_queries, all_selects)
        done.append(self)

        # LEFT JOINS FROM ROOT TO LEAF
        sql_selects = []
        sql_branch = [SQL_FROM]

        selects, leaf = nested_path[0].node_sql(all_selects)
        sql_selects.extend(selects)
        sql_branch.append(leaf)
        for step in nested_path[1:]:
            sql_branch.append(SQL_LEFT_JOIN)
            selects, leaf = step.node_sql(all_selects)
            sql_selects.extend(selects)
            sql_branch.append(leaf)
            sql_branch.append(SQL_ON)
            sql_branch.append(JoinSQL(
                SQL_AND,
                [
                    ConcatSQL(quote_column(f"i{step.id}_{i}"), SQL_EQ, quote_column(f"i{step.parent.id}_{i}"),)
                    for i, _ in enumerate(step.parent.uids)
                ],
            ))
        sql_branch.append(SQL_LEFT_JOIN)
        selects, leaf = self.leaf_sql(all_selects)
        sql_selects.extend(selects)
        sql_branch.append(leaf)
        sql_branch.append(SQL_ON)
        sql_branch.append(JoinSQL(
            SQL_AND,
            [
                ConcatSQL(quote_column(f"i{self.id}_{i}"), SQL_EQ, quote_column(f"i{self.parent.id}_{i}"),)
                for i, _ in enumerate(self.parent.uids)
            ],
        ))
        sql_queries.append(ConcatSQL(SQL_SELECT, sql_list(sql_selects), *sql_branch))
        return nested_path + (self,)


class SqlTree:
    def __init__(self, leaves: List[SqlStep]):
        self.leaves = leaves

    def to_sql(self):
        done = []
        all_selects = []
        for leaf in self.leaves:
            leaf.position(done, all_selects)

        done = []
        sql_queries = []
        for leaf in self.leaves:
            leaf.branch_sql(done, sql_queries, all_selects)

        ordering = [f"o{n.id}_{oi}" for n in done for oi, ov in enumerate(n.order + n.uids)]
        return ConcatSQL(
            JoinSQL(SQL_UNION_ALL, sql_queries),
            SQL_ORDERBY,
            JoinSQL(
                SQL_COMMA, [ConcatSQL(quote_column(o), SQL_IS_NOT_NULL, SQL_COMMA, quote_column(o)) for o in ordering]
            ),
        )

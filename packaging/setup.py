# encoding: utf-8
# THIS FILE IS AUTOGENERATED!
from setuptools import setup
setup(
    author='Kyle Lahnakoski',
    author_email='kyle@lahnakoski.com',
    classifiers=["Development Status :: 4 - Beta","Topic :: Software Development :: Libraries","Topic :: Software Development :: Libraries :: Python Modules","License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)","Topic :: Database","Topic :: Utilities","Programming Language :: SQL","Programming Language :: Python :: 3.8","Programming Language :: Python :: 3.9","Programming Language :: Python :: 3.11","Programming Language :: Python :: 3.12"],
    description='Multithreading for Sqlite, plus expression composition',
    extras_require={"tests":["mo-testing>=8.623.24125","beautifulsoup4>=4.12.3"]},
    include_package_data=True,
    install_requires=["jx-python==4.626.24125","mo-dots==10.623.24125","mo-files==6.624.24125","mo-future==7.584.24095","mo-imports==7.584.24095","mo-json==6.624.24125","mo-kwargs==7.623.24125","mo-logs==8.623.24125","mo-math==7.623.24125","mo-sql==4.624.24125","mo-sql==4.624.24125","mo-threads==6.624.24125","mo-times==5.623.24125"],
    license='MPL 2.0',
    long_description='# More SQLite!\n\nMultithreading for Sqlite, plus expression composition\n\n\n[![PyPI Latest Release](https://img.shields.io/pypi/v/mo-sqlite.svg)](https://pypi.org/project/mo-sqlite/)\n[![Build Status](https://github.com/klahnakoski/mo-sqlite/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/klahnakoski/mo-sqlite/actions/workflows/build.yml)\n[![Coverage Status](https://coveralls.io/repos/github/klahnakoski/mo-sqlite/badge.svg?branch=dev)](https://coveralls.io/github/klahnakoski/mo-sqlite?branch=dev)\n[![Downloads](https://pepy.tech/badge/mo-sqlite/month)](https://pepy.tech/project/mo-sqlite)\n\n\n## Multi-threaded Sqlite\n\nThis module wraps the `sqlite3.connection` with thread-safe traffic manager.  Here is typical usage: \n\n    from mo_sqlite import Sqlite\n    db = Sqlite("mydb.sqlite")\n    with db.transaction() as t:\n        t.command("insert into mytable values (1, 2, 3)")\n\nWhile you may have each thread own a `sqlite3.connection` to the same file, you will still get exceptions when another thread has the file locked.\n\n## Pull JSON out of database\n\nThis module includes a minimum experimental structure that can describe pulling deeply nested JSON documents out of a normalized database.  The tactic is to shape a single query who\'s resultset can be easily converted to the desired JSON by Python. Read more on [pulling json from a database](docs/JSON%20in%20Database.md)\n\nThere are multiple normal forms, including domain key normal form, and columnar form;  these have a multitude one-to-one relations, all represent the same logical schema, but differ in their access patterns to optimize for particular use cases.  This module intends to hide the particular database schema from the caller; exposing just the logical schema. \n\n\n\nThis experiment compliments the [mo-columns](https://github.com/klahnakoski/mo-columns) experiment, which is about pushing JSON into a database. \n   ',
    long_description_content_type='text/markdown',
    name='mo-sqlite',
    packages=["mo_sqlite","mo_sqlite.expressions"],
    url='https://github.com/klahnakoski/mo-sqlite',
    version='2.626.24125'
)
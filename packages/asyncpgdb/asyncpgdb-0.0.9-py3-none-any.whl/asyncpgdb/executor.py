from typing import Optional, Type, TypeVar
from asyncpgdb.sql import query_args
from asyncpgdb.row import row_parser, parse_row
from asyncpgdb.asyncpg import ConnectionAsyncpg

T = TypeVar("T")


async def _execute_query(query: str, vars: Optional[dict], func):
    qa = query_args(query=query, vars=vars)
    return await func(*qa.query_args())


async def fetch_var(
    query: str,
    vars: Optional[dict] = None,
    conn: ConnectionAsyncpg = None,
    row_class: Optional[Type[T]] = None,
):
    var = await _execute_query(query=query, vars=vars, func=conn.fetchval)
    return (
        var
        if row_class is None or var is None
        else parse_row(row_class=row_class, row=var)
    )


async def fetch_one(
    query: str,
    vars: Optional[dict] = None,
    conn: ConnectionAsyncpg = None,
    row_class: Type[T] = dict,
):
    row = await _execute_query(query=query, vars=vars, func=conn.fetchrow)
    return row if row is None else parse_row(row_class=row_class, row=row)


async def fetch_all(
    query: str,
    vars: Optional[dict] = None,
    conn: ConnectionAsyncpg = None,
    row_class: Type[T] = dict,
):
    rows = await _execute_query(query=query, vars=vars, func=conn.fetch)
    return list(map(row_parser(row_class=row_class), rows)) if rows else []


async def iter_all(
    query: str,
    vars: Optional[dict] = None,
    conn: ConnectionAsyncpg = None,
    row_class: Type[T] = dict,
):
    qa = query_args(query=query, vars=vars)
    async with conn.transaction():
        row_parser = row_parser(row_class=row_class)
        async for row in conn.cursor(*qa.query_args()):
            yield row_parser(row)


async def execute(
    query: str,
    vars: Optional[dict] = None,
    timeout: Optional[float] = None,
    conn: ConnectionAsyncpg = None,
):
    qa = query_args(query=query, vars=vars)
    result = None
    async with conn.transaction():
        result = await conn.execute(*qa.query_args(), timeout=timeout)
    if result is None:
        result = True
    return result


async def execute_many(
    query: str,
    vars_list: list[dict],
    timeout: Optional[float] = None,
    conn: ConnectionAsyncpg = None,
):
    result = None
    qa = query_args(command=query, vars_list=vars_list)

    async with conn.transaction():
        result = await conn.executemany(*qa.command_args(), timeout=timeout)
    if result is None:
        result = True
    return result

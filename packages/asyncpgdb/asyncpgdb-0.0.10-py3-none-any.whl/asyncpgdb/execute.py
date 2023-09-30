from abc import abstractmethod
from logging import Logger
from typing import Any, Callable, Coroutine, Optional, Type, TypeVar
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



class ExecuteProtocol:
    @abstractmethod
    async def acquire_connection(self) -> ConnectionAsyncpg:
        pass

    @abstractmethod
    async def release(self, __conn: ConnectionAsyncpg):
        pass

    def log_info(self, *args):
        logger = getattr(self, "_logger")
        if logger is not None and isinstance(logger, Logger):
            logger.info(*args)

    async def _process(self, method: Callable[..., Coroutine[Any, Any, T]], **kwargs):
        conn = await self.acquire_connection()
        kwargs["conn"] = conn
        try:
            result = await method(**kwargs)
        except Exception as error:
            self.log_info(f"Database.{method.__name__}.error: {str(error)}")
            result = None
        finally:
            await self.release(conn)
        return result

    async def _process_iter(
        self, method: Callable[..., Coroutine[Any, Any, T]], **kwargs
    ):
        conn = await self.acquire_connection()
        kwargs["conn"] = conn
        try:
            async for obj in method(**kwargs):
                yield obj

        except Exception as error:
            self.log_info(f"Database.{method.__name__}.error: {str(error)}")

        finally:
            await self.release(conn)

    async def fetch_var(
        self,
        query: str,
        vars: Optional[dict] = None,
        row_class: Optional[Type[T]] = None,
    ):
        return await self._process(
            method=fetch_var, query=query, vars=vars, row_class=row_class
        )

    async def fetch_one(
        self, query: str, vars: Optional[dict] = None, row_class: Type[T] = dict
    ):
        return await self._process(
            method=fetch_one, query=query, vars=vars, row_class=row_class
        )

    async def fetch_all(
        self, query: str, vars: Optional[dict] = None, row_class: Type[T] = dict
    ):
        return await self._process(
            method=fetch_all, query=query, vars=vars, row_class=row_class
        )

    async def iter_all(
        self, query: str, vars: Optional[dict] = None, row_class: Type[T] = dict
    ):
        async for obj in self._process_iter(
            method=iter_all, query=query, vars=vars, row_class=row_class
        ):
            yield obj

    async def execute(
        self,
        query: str,
        vars: Optional[dict] = None,
        timeout: Optional[float] = None,
    ):
        return await self._process(
            method=execute, query=query, vars=vars, timeout=timeout
        )

    async def execute_many(
        self,
        query: str,
        vars_list: list[dict],
        timeout: Optional[float] = None,
    ):
        result = None
        if vars_list:
            result = await self._process(
                method=execute_many,
                query=query,
                vars_list=vars_list,
                timeout=timeout,
            )
        return result

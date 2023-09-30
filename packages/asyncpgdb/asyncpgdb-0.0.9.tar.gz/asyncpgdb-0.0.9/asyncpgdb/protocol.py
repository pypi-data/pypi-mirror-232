from typing import Any, Callable, Coroutine, Optional, Type, TypeVar
from abc import abstractmethod
from logging import Logger
from asyncpgdb.asyncpg import ConnectionAsyncpg
from asyncpgdb.executor import (
    execute,
    execute_many,
    fetch_var,
    fetch_one,
    fetch_all,
    iter_all,
)

T = TypeVar("T")


class ExecutorProtocol:
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
        if vars_list:
            result = await self._process(
                method=execute_many,
                query=query,
                vars_list=vars_list,
                timeout=timeout,
            )
        else:
            result = None
        return result

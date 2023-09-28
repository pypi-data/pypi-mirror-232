from typing import Any, Optional, Type, TypeVar
from logging import Logger
from pydantic import BaseModel, BaseConfig
import asyncpg
from asyncpg.connection import Connection
from asyncpgdb.protocol import ExecutorProtocol

T = TypeVar("T")


class DatabaseSettings(BaseModel):
    class Config(BaseConfig):
        arbitrary_types_allowed = True

    dsn: str
    min_size: int
    max_size: int
    max_queries: int
    command_timeout: int
    max_inactive_connection_lifetime: float
    setup: Optional[Any]
    init: Optional[Any]
    loop: Optional[Any]
    ssl: Optional[str]
    connection_class: Type[Connection]
    record_class: Optional[Type]


class Database(ExecutorProtocol):
    def __init__(
        self,
        dsn: str,
        min_size: int = 2,
        max_size: int = 60,
        command_timeout: int = 60,
        max_queries: int = 50000,
        max_inactive_connection_lifetime: float = 300,
        setup: Optional[Any] = None,
        init: Optional[Any] = None,
        loop: Optional[Any] = None,
        connection_class: Type[Connection] = Connection,
        record_class: Optional[Type] = None,
        logger: Optional[Logger] = None,
        ssl: Optional[str] = None,  # ("require",)
        **connect_kwargs: Any,
    ):
        self._settings = DatabaseSettings(
            dsn=dsn,
            min_size=min_size,
            max_size=max_size,
            command_timeout=command_timeout,
            max_queries=max_queries,
            max_inactive_connection_lifetime=max_inactive_connection_lifetime,
            setup=setup,
            init=init,
            loop=loop,
            connection_class=connection_class,
            record_class=record_class,
            ssl=ssl,
        )
        self._pool = None
        self._logger = logger

    def _log_exception(self, *args):
        if self._logger is not None:
            self._logger.exception(*args)

    async def connect(self):
        if not self._pool:
            try:
                self._pool = await asyncpg.create_pool(**self._settings.dict(exclude_unset=True, exclude_none=True))
                self.log_info("Database pool connection opened")

            except Exception as err:
                self._log_exception(err)

    async def acquire_connection(self) -> Connection:
        try:
            await self.connect()
            result = await self._pool.acquire()
            if not isinstance(result, Connection):
                raise ValueError(
                    f"pool connection is not asyncpg.connection.Connection; {str(type(result))}"
                )
        except Exception as error:
            self._log_exception(f"Error creating connection:", error)

        return result


    async def release(self, __conn: Connection):
        await self._pool.release(__conn)


    async def close(self):
        if not self._pool:
            try:
                await self._pool.close()
                self.log_info("Database pool connection closed")
            except Exception as err:
                self._log_exception(err)

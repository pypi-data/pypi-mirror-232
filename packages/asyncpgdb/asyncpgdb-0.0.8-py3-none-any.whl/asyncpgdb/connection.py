from typing import Any, Optional, Type, Union
from logging import Logger
from pydantic import BaseModel, BaseConfig
from asyncpg import connect, connection
from asyncpgdb.protocol import ExecutorProtocol
from asyncpgdb.util.dsn import create_dsn


class ConnectionSettings(BaseModel):
    class Config(BaseConfig):
        arbitrary_types_allowed = True

    dsn: Optional[str]
    host: Optional[str]
    port: Optional[str]
    user: Optional[str]
    password: Optional[str]
    passfile: Optional[str]
    database: Optional[str]
    loop: Optional[Any]
    timeout: Optional[float]
    statement_cache_size: Optional[int]
    max_cached_statement_lifetime: Optional[float]
    max_cacheable_statement_size: Optional[int]
    command_timeout: Optional[float]
    ssl: Optional[str]
    direct_tls: bool
    connection_class: Type[connection.Connection]
    record_class: Optional[Type]
    server_settings: Optional[dict]


class Connection(ExecutorProtocol):
    def __init__(
        self,
        dsn: Optional[str] = None,
        *,
        host: Optional[str] = None,
        port: Optional[Union[str, int]] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        passfile: Optional[str] = None,
        database: Optional[str] = None,
        loop: Optional[Any] = None,
        timeout: Optional[float] = 60,
        statement_cache_size: Optional[int] = 100,
        max_cached_statement_lifetime: Optional[float] = 300,
        max_cacheable_statement_size: Optional[int] = 1024 * 15,
        command_timeout: Optional[float] = None,
        ssl: Optional[str] = None,
        direct_tls: bool = False,
        connection_class: Type[connection.Connection] = connection.Connection,
        record_class: Optional[Type] = None,
        server_settings: Optional[dict] = None,
        conn: Optional[connection.Connection] = None,
        logger: Optional[Logger] = None,
    ):
        if not dsn:
            dsn = create_dsn(
                host=host, port=port, user=user, password=password, database=database
            )
        self._settings = ConnectionSettings(
            dsn=dsn,
            host=host,
            port=port,
            user=user,
            password=password,
            passfile=passfile,
            database=database,
            loop=loop,
            timeout=timeout,
            statement_cache_size=statement_cache_size,
            max_cacheable_statement_size=max_cacheable_statement_size,
            max_cached_statement_lifetime=max_cached_statement_lifetime,
            command_timeout=command_timeout,
            ssl=ssl,
            direct_tls=direct_tls,
            connection_class=connection_class,
            record_class=record_class,
            server_settings=server_settings,
        )

        self._conn = conn
        self._logger = logger

    async def acquire_connection(self) -> connection.Connection:
        if self._conn is None or self._conn.is_closed():
            self._conn = await connect(
                **self._settings.dict(exclude_none=True, exclude_unset=True)
            )

        return self._conn

    async def close(self):
        if self._conn is not None and not self._conn.is_closed():
            await self._conn.close()
            self._conn = None


    async def release(self, __conn: connection.Connection):
        pass

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession

URL = "sqlite+aiosqlite:///weather.db"

def create_db_engine() -> AsyncEngine:
    return create_async_engine(
        URL,
        connect_args={"check_same_thread": False}
    )

def get_session_factory(engine: AsyncEngine) -> AsyncSession:
    return async_sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False
    )


from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.config import config

# echo = config.ENVIRONMENT == Environment.LOCAL
echo = False

# an Engine, which the Session will use for connection resources
async_engine = create_async_engine(
    url=str(config.DB_URL),
    # Enable connection health checks before returning connections from the pool
    pool_pre_ping=True,
    # Control SQLAlchemy's logging of all SQL statements
    echo=echo,
    # Set the number of connections to keep open in the pool
    pool_size=20,
    # Allow additional connections beyond pool_size for short bursts
    max_overflow=30,
    # Maximum time (in seconds) to wait for a connection to become available
    pool_timeout=30,  # Prevents hanging indefinitely if the pool is exhausted
    # Time (in seconds) after which connections are recycled to avoid stale connections
    pool_recycle=1800,  # Recycle connections every 30 minutes
)


AsyncSessionLocal = async_sessionmaker(bind=async_engine, autocommit=False, autoflush=False, expire_on_commit=False)

import redis
from loguru import logger

from src.core.config import config


def redis_connect(db: int = config.REDIS_DB) -> redis.client.Redis | None:
    try:
        client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=db,
            socket_timeout=5,
        )
        ping = client.ping()
        if ping is True:
            return client
    except redis.AuthenticationError:
        logger.error("AuthenticationError")
        raise Exception("Cannot connect to Redis")


cache = redis_connect()
task_queue = redis_connect(db=config.REDIS_TASK_QUEUE_DB)

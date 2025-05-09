from rq import Queue
from rq_dashboard_fast import RedisQueueDashboard

from src.core.config import config
from src.core.helpers.redis import task_queue

# Add a seperate queue for emails and other tasks
queue = Queue(connection=task_queue)

# Rq Dashboard
dashboard = RedisQueueDashboard(
    redis_url=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_TASK_QUEUE_DB}",
    path="/rq",
)

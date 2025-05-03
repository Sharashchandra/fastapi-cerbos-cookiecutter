from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from rq.exceptions import NoSuchJobError
from rq.job import Job, JobStatus

from src.core.helpers.redis import task_queue
from src.core.helpers.rq import queue
from src.users.jobs.preload_blacklisted_tokens import PreloadBlacklistedTokens

preload_config = [
    {
        "job_id": "preload_blacklisted_tokens_on_startup",
        "fn": PreloadBlacklistedTokens().run,
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    for config in preload_config:
        try:
            job = Job.fetch(id=config["job_id"], connection=task_queue)
            if job.get_status() == JobStatus.FAILED:
                logger.info(f"Preloading {config['job_id']} on startup because previous job failed")
                queue.enqueue(config["fn"], job_id=config["job_id"])
        except NoSuchJobError:
            logger.info(f"Preloading {config['job_id']} on startup")
            queue.enqueue(config["fn"], job_id=config["job_id"])

    yield

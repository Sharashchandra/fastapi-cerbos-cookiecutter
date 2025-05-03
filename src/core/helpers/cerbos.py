from cerbos.sdk.grpc.client import AsyncCerbosClient

from src.core.config import config

cerbos_client = AsyncCerbosClient(config.CERBOS_URL)

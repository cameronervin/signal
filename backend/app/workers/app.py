import asyncio
import threading
from typing import Any

import httpx
from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown, worker_ready

from app.agents.graph_provider import (
    SignalGraphProvider,
    clear_signal_graph_provider_cache,
    get_signal_graph_provider,
)
from app.core.config import get_settings
from app.infrastructure.llm import clear_llm_provider_cache, get_llm_provider
from app.infrastructure.public_data import (
    PublicDataClient,
    clear_public_data_client_cache,
    create_public_data_client,
)

settings = get_settings()

celery_app = Celery(
    "signal",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)
celery_app.conf.update(
    accept_content=["json"],
    result_expires=3600,
    result_serializer="json",
    task_serializer="json",
    timezone="UTC",
)

_worker_loop: asyncio.AbstractEventLoop | None = None
_worker_loop_owner_thread: int | None = None
_worker_resources_initialized = False
_worker_http_client: httpx.AsyncClient | None = None
_worker_public_data_client: PublicDataClient | None = None
_worker_graph_provider: SignalGraphProvider | None = None
_worker_llm_provider: Any | None = None


def run_async(coro):
    if _worker_loop is None:
        return asyncio.run(coro)
    if threading.get_ident() != _worker_loop_owner_thread:
        return asyncio.run(coro)
    if _worker_loop.is_running() or _worker_loop.is_closed():
        return asyncio.run(coro)
    return _worker_loop.run_until_complete(coro)


def get_worker_resources() -> tuple[SignalGraphProvider, PublicDataClient] | None:
    if _worker_graph_provider is None or _worker_public_data_client is None:
        return None
    return _worker_graph_provider, _worker_public_data_client


@worker_process_init.connect
@worker_ready.connect
def init_worker_resources(**_: object) -> None:
    global _worker_loop
    global _worker_loop_owner_thread
    global _worker_resources_initialized
    global _worker_http_client
    global _worker_public_data_client
    global _worker_graph_provider
    global _worker_llm_provider

    if _worker_resources_initialized:
        return

    _worker_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_worker_loop)
    _worker_loop_owner_thread = threading.get_ident()
    _worker_http_client = httpx.AsyncClient(follow_redirects=True)
    _worker_public_data_client = create_public_data_client(
        settings,
        http_client=_worker_http_client,
    )
    _worker_llm_provider = get_llm_provider(settings)
    _worker_graph_provider = get_signal_graph_provider(settings=settings)
    _worker_graph_provider.signal_graph()
    _worker_resources_initialized = True


@worker_process_shutdown.connect
def teardown_worker_resources(**_: object) -> None:
    global _worker_loop
    global _worker_loop_owner_thread
    global _worker_resources_initialized
    global _worker_http_client
    global _worker_public_data_client
    global _worker_graph_provider
    global _worker_llm_provider

    if _worker_http_client is not None:
        if _worker_loop is not None and not _worker_loop.is_closed():
            _worker_loop.run_until_complete(_worker_http_client.aclose())
        else:
            asyncio.run(_worker_http_client.aclose())
    if _worker_loop is not None and not _worker_loop.is_closed():
        _worker_loop.close()
    asyncio.set_event_loop(None)

    _worker_loop = None
    _worker_loop_owner_thread = None
    _worker_resources_initialized = False
    _worker_http_client = None
    _worker_public_data_client = None
    _worker_graph_provider = None
    _worker_llm_provider = None
    clear_public_data_client_cache()
    clear_llm_provider_cache()
    clear_signal_graph_provider_cache()

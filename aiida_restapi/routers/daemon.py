"""Declaration of FastAPI router for daemon endpoints."""

from __future__ import annotations

import time

from aiida.cmdline.utils.decorators import with_dbenv
from aiida.engine.daemon.client import DaemonException, get_daemon_client
from fastapi import APIRouter

from aiida_restapi.jsonapi.models import errors
from aiida_restapi.models.daemon import DaemonStatus, DaemonWorker

_WORKER_CHANGE_TIMEOUT = 5.0
_WORKER_POLL_INTERVAL = 0.1

read_router = APIRouter(prefix='/daemon')
write_router = APIRouter(prefix='/daemon')


@read_router.get(
    '/status',
    response_model=DaemonStatus,
    responses={
        500: {'model': errors.DaemonError},
    },
)
@with_dbenv()
async def get_daemon_status() -> DaemonStatus:
    """Return the daemon status."""
    client = get_daemon_client()

    if not client.is_daemon_running:
        return DaemonStatus(running=False, num_workers=None)

    response = client.get_numprocesses()

    return DaemonStatus(running=True, num_workers=response['numprocesses'])


@read_router.get(
    '/worker',
    response_model=dict[str, DaemonWorker],
    responses={
        500: {'model': errors.DaemonError},
    },
)
@with_dbenv()
async def get_daemon_worker() -> dict[str, DaemonWorker]:
    """Return daemon worker metadata."""
    client = get_daemon_client()

    if not client.is_daemon_running:
        return {}

    response = client.get_worker_info()

    return response['info']


@write_router.post(
    '/start',
    response_model=DaemonStatus,
    responses={
        500: {'model': errors.DaemonError},
    },
)
@with_dbenv()
async def start_daemon() -> DaemonStatus:
    """Start the daemon."""
    client = get_daemon_client()

    if client.is_daemon_running:
        raise DaemonException('The daemon is already running.')

    client.start_daemon()
    response = client.get_numprocesses()

    return DaemonStatus(running=True, num_workers=response['numprocesses'])


@write_router.post(
    '/stop',
    response_model=DaemonStatus,
    responses={
        500: {'model': errors.DaemonError},
    },
)
@with_dbenv()
async def stop_daemon() -> DaemonStatus:
    """Stop the daemon."""
    client = get_daemon_client()

    if not client.is_daemon_running:
        raise DaemonException('The daemon is not running.')

    client.stop_daemon()

    return DaemonStatus(running=False, num_workers=None)


@write_router.post(
    '/restart',
    response_model=DaemonStatus,
    responses={
        500: {'model': errors.DaemonError},
    },
)
@with_dbenv()
async def restart_daemon() -> DaemonStatus:
    """Restart the daemon."""
    client = get_daemon_client()

    if not client.is_daemon_running:
        raise DaemonException('The daemon is not running.')

    client.restart_daemon()

    return DaemonStatus(running=True, num_workers=client.get_numprocesses()['numprocesses'])


def _wait_for_num_workers(
    target: int,
    timeout: float = _WORKER_CHANGE_TIMEOUT,
    interval: float = _WORKER_POLL_INTERVAL,
) -> int:
    """Wait for the daemon worker count to reach ``target`` and return the observed value."""
    deadline = time.monotonic() + timeout
    client = get_daemon_client()

    while True:
        current = client.get_numprocesses()['numprocesses']
        if current == target:
            return current

        if time.monotonic() >= deadline:
            return current

        time.sleep(interval)


@write_router.post(
    '/increase',
    response_model=DaemonStatus,
    responses={
        500: {'model': errors.DaemonError},
    },
)
@with_dbenv()
async def increase_daemon_worker() -> DaemonStatus:
    """Increase the number of daemon workers by one."""
    client = get_daemon_client()

    if not client.is_daemon_running:
        raise DaemonException('The daemon is not running.')

    initial = client.get_numprocesses()['numprocesses']
    client.increase_workers(1)
    num_workers = _wait_for_num_workers(initial + 1)

    return DaemonStatus(running=True, num_workers=num_workers)


@write_router.post(
    '/decrease',
    response_model=DaemonStatus,
    responses={
        500: {'model': errors.DaemonError},
    },
)
@with_dbenv()
async def decrease_daemon_worker() -> DaemonStatus:
    """Decrease the number of daemon workers by one."""
    client = get_daemon_client()

    if not client.is_daemon_running:
        raise DaemonException('The daemon is not running.')

    initial = client.get_numprocesses()['numprocesses']
    client.decrease_workers(1)
    num_workers = _wait_for_num_workers(max(initial - 1, 0))

    return DaemonStatus(running=True, num_workers=num_workers)

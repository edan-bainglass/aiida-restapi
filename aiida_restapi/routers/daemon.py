"""Declaration of FastAPI router for daemon endpoints."""

from __future__ import annotations

import asyncio
import time
import typing as t

from aiida.cmdline.utils.decorators import with_dbenv
from aiida.engine.daemon.client import DaemonException, get_daemon_client
from fastapi import APIRouter, Query

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
    '/workers',
    response_model=dict[str, DaemonWorker],
    responses={
        500: {'model': errors.DaemonError},
    },
)
@with_dbenv()
async def get_daemon_workers() -> dict[str, dict[str, t.Any]]:
    """Return daemon workers metadata."""
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
async def start_daemon() -> dict[str, t.Any]:
    """Start the daemon."""
    client = get_daemon_client()

    if client.is_daemon_running:
        raise DaemonException('The daemon is already running.')

    client.start_daemon()
    response = client.get_numprocesses()

    return {
        'running': True,
        'num_workers': response['numprocesses'],
    }


@write_router.post(
    '/stop',
    response_model=DaemonStatus,
    responses={
        500: {'model': errors.DaemonError},
    },
)
@with_dbenv()
async def stop_daemon() -> dict[str, t.Any]:
    """Stop the daemon."""
    client = get_daemon_client()

    if not client.is_daemon_running:
        raise DaemonException('The daemon is not running.')

    client.stop_daemon()

    return {
        'running': False,
        'num_workers': None,
    }


@write_router.post(
    '/restart',
    response_model=DaemonStatus,
    responses={
        500: {'model': errors.DaemonError},
    },
)
@with_dbenv()
async def restart_daemon() -> dict[str, t.Any]:
    """Restart the daemon."""
    client = get_daemon_client()

    if not client.is_daemon_running:
        raise DaemonException('The daemon is not running.')

    client.restart_daemon()

    return {
        'running': True,
        'num_workers': client.get_numprocesses()['numprocesses'],
    }


async def _wait_for_num_workers(
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

        await asyncio.sleep(interval)


@write_router.post(
    '/increase',
    response_model=DaemonStatus,
    responses={
        500: {'model': errors.DaemonError},
    },
)
@with_dbenv()
async def increase_daemon_workers(
    amount: t.Annotated[
        int,
        Query(
            description='The number of workers to increase by',
            ge=1,
        ),
    ] = 1,
) -> dict[str, t.Any]:
    """Increase the number of daemon workers by a specified amount (default=1)."""
    client = get_daemon_client()

    if not client.is_daemon_running:
        raise DaemonException('The daemon is not running.')

    initial = client.get_numprocesses()['numprocesses']
    client.increase_workers(amount)
    num_workers = await _wait_for_num_workers(initial + amount)

    return {
        'running': True,
        'num_workers': num_workers,
    }


@write_router.post(
    '/decrease',
    response_model=DaemonStatus,
    responses={
        500: {'model': errors.DaemonError},
    },
)
@with_dbenv()
async def decrease_daemon_workers(
    amount: t.Annotated[
        int,
        Query(
            description='The number of workers to decrease by',
            ge=1,
        ),
    ] = 1,
) -> dict[str, t.Any]:
    """Decrease the number of daemon workers by a specified amount (default=1)."""
    client = get_daemon_client()

    if not client.is_daemon_running:
        raise DaemonException('The daemon is not running.')

    initial = client.get_numprocesses()['numprocesses']
    client.decrease_workers(amount)
    num_workers = await _wait_for_num_workers(max(initial - amount, 0))

    return {
        'running': True,
        'num_workers': num_workers,
    }

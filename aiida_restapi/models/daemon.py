import typing as t

import pydantic as pdt


class DaemonStatus(pdt.BaseModel):
    """Response model for daemon status."""

    running: bool = pdt.Field(
        description='Whether the daemon is running or not.',
        examples=[True, False],
    )
    num_workers: t.Optional[int] = pdt.Field(
        description='The number of workers if the daemon is running.',
        examples=[1, 2, 3],
    )


class DaemonWorker(pdt.BaseModel):
    """Response model for daemon worker metadata."""

    pid: int = pdt.Field(
        description='The process identifier of the worker process.',
        examples=[12345],
    )
    mem: float = pdt.Field(
        description='The memory usage percentage for the worker process.',
        examples=[12.5],
    )
    cpu: float = pdt.Field(
        description='The CPU usage percentage for the worker process.',
        examples=[25.0],
    )
    started: float = pdt.Field(
        description='Unix timestamp when the worker process started.',
        examples=[1697040000.0],
    )

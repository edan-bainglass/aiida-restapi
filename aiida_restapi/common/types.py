"""Common type variables."""

from __future__ import annotations

import typing as t

from aiida import orm
from fastapi import Request, Response
from fastapi import exceptions as fastapi_exceptions

EntityType = t.TypeVar('EntityType', bound='orm.Entity')
EntityModelType = t.TypeVar('EntityModelType', bound='orm.OrmModel')

NodeType = t.TypeVar('NodeType', bound='orm.Node')
NodeModelType = t.TypeVar('NodeModelType', bound='orm.Node.BaseNodeModel')

RequestValidationErrorHandler = t.Callable[
    [
        Request,
        fastapi_exceptions.RequestValidationError,
    ],
    Response | None,
]

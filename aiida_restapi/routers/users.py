"""Declaration of FastAPI router for users."""

from __future__ import annotations

import typing as t

from aiida import orm
from aiida.cmdline.utils.decorators import with_dbenv
from fastapi import APIRouter, Depends, Query, Request
from pydantic import PlainValidator

from aiida_restapi.common import query
from aiida_restapi.jsonapi.adapters import JsonApiAdapter as JsonApi
from aiida_restapi.jsonapi.models import errors
from aiida_restapi.jsonapi.models.aiida import UserCollectionDocument, UserResourceDocument
from aiida_restapi.jsonapi.responses import JsonApiResponse
from aiida_restapi.services.entity import EntityService

read_router = APIRouter(prefix='/users')
write_router = APIRouter(prefix='/users')

service = EntityService[orm.User, orm.User.ReadModel](orm.User)


def validate_user_email(value: str) -> str:
    if value.count('@') != 1:
        raise ValueError('Invalid email address - must contain exactly one "@"')
    return value


UserEmail: t.TypeAlias = t.Annotated[str, PlainValidator(validate_user_email)]
UserIdentifier: t.TypeAlias = int | UserEmail


@read_router.get(
    '/schema',
    response_model=dict[str, t.Any],
    responses={
        422: {'model': errors.RequestValidationError, 'description': 'Validation Error'},
    },
)
async def get_users_schema(
    which: t.Annotated[
        t.Literal['read', 'write'],
        Query(description='Type of schema to retrieve: "read" or "write"'),
    ] = 'read',
) -> dict[str, t.Any]:
    """Get JSON schema for AiiDA users."""
    return service.get_schema(which=which)


@read_router.get(
    '/projections',
    response_model=list[str],
)
async def get_user_projections() -> list[str]:
    """Get queryable projections for AiiDA users."""
    return service.get_projections()


@read_router.get(
    '',
    response_class=JsonApiResponse,
    response_model=UserCollectionDocument,
    response_model_exclude_none=True,
    responses={
        422: {
            'model': t.Union[errors.RequestValidationError, errors.QueryBuilderError],
            'description': 'Validation Error | Query Builder Error',
        },
    },
)
@with_dbenv()
async def get_users(
    request: Request,
    query_params: t.Annotated[
        query.CollectionQueryParams,
        Depends(query.collection_query_params),
    ],
) -> dict[str, t.Any]:
    """Get AiiDA users with optional filtering, sorting, and/or pagination."""
    results = service.get_many(query_params)
    return JsonApi.collection(
        request,
        results,
        resource_identity=orm.User.identity_field,
        resource_type='users',
        query_params=query_params,
    )


@read_router.get(
    '/{identifier}',
    response_class=JsonApiResponse,
    response_model=UserResourceDocument,
    response_model_exclude_none=True,
    responses={
        404: {'model': errors.NonExistentError, 'description': 'Resource Not Found'},
        409: {'model': errors.MultipleObjectsError, 'description': 'Multiple Resources Found'},
        422: {'model': errors.RequestValidationError, 'description': 'Validation Error'},
    },
)
@with_dbenv()
async def get_user(
    request: Request,
    identifier: UserIdentifier,
    query_params: t.Annotated[
        query.ResourceQueryParams,
        Depends(query.resource_query_params),
    ],
) -> dict[str, t.Any]:
    """Get AiiDA user."""
    # HACK AiiDA User does not have a UUID - see https://github.com/aiidateam/aiida-core/issues/6174
    key = 'pk' if isinstance(identifier, int) else 'email'
    print(key, identifier)
    user = orm.User.collection.get(**{key: identifier})  # we need the EntityIdentifier-compatible user pk
    assert user.pk  # appeasing mypy - something is terribly wrong if pk is None!
    result = service.get_one(user.pk)
    return JsonApi.resource(
        request,
        result,
        resource_identity=orm.User.identity_field,
        resource_type='users',
        include=query_params.include,
    )


@write_router.post(
    '',
    response_model=UserResourceDocument,
    response_class=JsonApiResponse,
    response_model_exclude_none=True,
    responses={
        403: {'model': errors.StoringNotAllowedError, 'description': 'Storing Not Allowed'},
        422: {
            'model': t.Union[errors.RequestValidationError, errors.InvalidInputError],
            'description': 'Validation Error | Invalid Input',
        },
    },
)
@with_dbenv()
async def create_user(
    request: Request,
    user_model: orm.User.WriteModel,
) -> dict[str, t.Any]:
    """Create new AiiDA user."""
    result = service.add(user_model)
    return JsonApi.resource(
        request,
        result,
        resource_identity=orm.User.identity_field,
        resource_type='users',
    )

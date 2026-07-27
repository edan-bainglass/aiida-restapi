"""Responses module."""

from __future__ import annotations

import typing as t

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


class EncodedJsonResponse(JSONResponse):
    """JSONResponse that encodes its content as jsonable."""

    def render(self, content: t.Any) -> bytes:
        content = jsonable_encoder(content, exclude_none=True)
        return super().render(content)


class JsonApiResponse(EncodedJsonResponse):
    """JSONResponse for JSON:API media type."""

    media_type = 'application/vnd.api+json'


class JsonSchemaResponse(EncodedJsonResponse):
    """JSONResponse for JSON Schema media type."""

    media_type = 'application/schema+json'

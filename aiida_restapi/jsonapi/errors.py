from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request

from .models.base import JsonApiErrorDocument
from .responses import JsonApiResponse


def jsonapi_error(
    request: Request,
    exception: Exception,
    status_code: int,
) -> JsonApiResponse:
    """Generate a JSON:API compliant error response.

    :param request: The incoming request.
    :type request: Request
    :param exception: The exception that was raised.
    :type exception: Exception
    :param status_code: The HTTP status code for the response.
    :type status_code: int
    :return: A JSON response containing the error in JSON:API format.
    :rtype: JsonApiResponse
    """
    return JsonApiResponse(
        status_code=status_code,
        content=jsonable_encoder(
            obj=JsonApiErrorDocument(
                links={
                    'self': str(request.url),
                },
                errors=[
                    {
                        'title': exception.__class__.__name__,
                        'status': str(status_code),
                        'detail': str(exception),
                    },
                ],
            ),
            exclude_none=True,
        ),
    )

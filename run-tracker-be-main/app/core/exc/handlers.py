import json

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.exc.base import (
    BadRequestException,
    ForbiddenException,
    ObjectAlreadyExistsException,
    ObjectNotFoundException,
    ServerErrorException,
    UnauthorizedException,
)


def handle_object_not_found(_: Request, e: ObjectNotFoundException) -> JSONResponse:
    return JSONResponse(
        content={"message": str(e)}, status_code=status.HTTP_404_NOT_FOUND
    )


def handle_bad_request(_: Request, e: BadRequestException) -> JSONResponse:
    return JSONResponse(
        content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST
    )


def handle_object_already_exists(
    _: Request, e: ObjectAlreadyExistsException
) -> JSONResponse:
    return JSONResponse(
        content={"message": str(e)}, status_code=status.HTTP_409_CONFLICT
    )


def handle_validation_error(_: Request, e: ValidationError) -> JSONResponse:
    return JSONResponse(
        content=json.loads(e.json()), status_code=status.HTTP_400_BAD_REQUEST
    )


def handle_server_error(_: Request, e: ServerErrorException) -> JSONResponse:
    return JSONResponse(
        content={"message": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def handle_unauthorized(_: Request, e: UnauthorizedException) -> JSONResponse:
    return JSONResponse(
        content={"message": str(e)}, status_code=status.HTTP_401_UNAUTHORIZED
    )


def handle_forbidden(_: Request, e: ForbiddenException) -> JSONResponse:
    return JSONResponse(
        content={"message": str(e)}, status_code=status.HTTP_403_FORBIDDEN
    )

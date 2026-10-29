"""Centralized exception handlers for application exceptions."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.custom_exceptions import (
    ConflictError,
    DatabaseError,
    ForbiddenError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
    JWTConfigurationError,
    NotFoundError,
)

logger = logging.getLogger(__name__)


async def handle_jwt_configuration_error(
    request: Request,
    _exc: JWTConfigurationError,
) -> JSONResponse:
    """Handle JWTConfigurationError by logging and returning a safe HTTP 500 response."""
    logger.error(
        "JWT configuration error (%s) for %s %s",
        type(_exc).__name__,
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server configuration error"},
    )


async def handle_invalid_access_token(
    request: Request,
    exc: InvalidAccessTokenError,
) -> JSONResponse:
    """Handle InvalidAccessTokenError by returning an HTTP 401 response."""
    logger.warning(
        "Invalid access token for %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def handle_conflict_error(
    request: Request,
    exc: ConflictError,
) -> JSONResponse:
    """Handle application conflicts by returning an HTTP 409 response."""
    logger.warning(
        "Application conflict for %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=409,
        content={"detail": exc.message},
    )


async def handle_not_found_error(
    request: Request,
    exc: NotFoundError,
) -> JSONResponse:
    """Handle missing resources with an HTTP 404 response."""
    logger.info(
        "Resource not found for %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message},
    )


async def handle_database_error(
    request: Request,
    exc: DatabaseError,
) -> JSONResponse:
    """Log the database cause and return a generic HTTP 500 response."""
    cause = exc.__cause__
    if cause is not None:
        logger.error(
            "Database operation failed for %s %s: %s",
            request.method,
            request.url.path,
            cause,
            exc_info=(type(cause), cause, cause.__traceback__),
        )
    else:
        logger.error(
            "Database operation failed for %s %s without a chained cause",
            request.method,
            request.url.path,
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred"},
    )


async def handle_invalid_credentials_error(
    request: Request,
    exc: InvalidCredentialsError,
) -> JSONResponse:
    """Handle invalid credentials with an HTTP 401 response."""
    logger.warning(
        "Invalid credentials for %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def handle_forbidden_error(
    request: Request,
    exc: ForbiddenError,
) -> JSONResponse:
    """Handle authorization failures with an HTTP 403 response."""
    logger.warning(
        "Forbidden request for %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=403,
        content={"detail": exc.message},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all centralized application exception handlers with FastAPI."""
    app.add_exception_handler(
        JWTConfigurationError,
        handle_jwt_configuration_error,
    )
    app.add_exception_handler(
        InvalidAccessTokenError,
        handle_invalid_access_token,
    )
    app.add_exception_handler(
        NotFoundError,
        handle_not_found_error,
    )
    app.add_exception_handler(
        ConflictError,
        handle_conflict_error,
    )
    app.add_exception_handler(
        DatabaseError,
        handle_database_error,
    )
    app.add_exception_handler(
        InvalidCredentialsError,
        handle_invalid_credentials_error,
    )
    app.add_exception_handler(
        ForbiddenError,
        handle_forbidden_error,
    )

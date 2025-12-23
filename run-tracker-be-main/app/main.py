import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import ValidationError

from app.core import exc
from app.core.config import settings
from app.core.exc import handlers
from app.routers import router


def _configure_logging() -> None:
    """
    Configures logging for the application using Loguru.
    """
    logger.add(
        "app/app.log",
        rotation="100 MB",
        retention="7 days",
        level="INFO",
        serialize=True,
    )


def _add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        exc.ObjectAlreadyExistsException, handlers.handle_object_already_exists
    )
    app.add_exception_handler(
        exc.ObjectNotFoundException, handlers.handle_object_not_found
    )
    app.add_exception_handler(exc.BadRequestException, handlers.handle_bad_request)
    app.add_exception_handler(ValidationError, handlers.handle_validation_error)
    app.add_exception_handler(exc.ServerErrorException, handlers.handle_server_error)
    app.add_exception_handler(exc.UnauthorizedException, handlers.handle_unauthorized)
    app.add_exception_handler(exc.ForbiddenException, handlers.handle_forbidden)


def _add_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-CAPTCHA-Required"],
    )


def create_app() -> FastAPI:
    _app = FastAPI(title=settings.app.PROJECT_NAME)

    _app.include_router(router)
    _add_middleware(_app)
    _configure_logging()
    _add_exception_handlers(_app)

    return _app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        reload=settings.app.RELOAD,
        host=settings.app.HOST,
        port=settings.app.PORT,
    )

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.core.db import engine

router = APIRouter()


@router.get("", description="Check App availability.")
async def healthcheck() -> JSONResponse:
    return JSONResponse(content="Server works")


@router.get("/db", description="Check Postgres availability.")
async def database_healthcheck() -> JSONResponse:
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {e}",
        )

    return JSONResponse(content="Database works")

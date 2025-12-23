from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.dependencies import CurrentUserDep, RunServiceDep, UnitOfWorkDep
from app.enums.run import RunSortBy, SortOrder
from app.enums.statistics import StatisticsPeriod
from app.schemas.runs import (
    RunCreateRequest,
    RunListResponse,
    RunResponse,
    RunUpdateRequest,
)

router = APIRouter()


@router.post("/", response_model=RunResponse, status_code=201)
async def create_run(
    current_user: CurrentUserDep,
    data: RunCreateRequest,
    run_service: RunServiceDep,
    uow: UnitOfWorkDep,
) -> RunResponse:
    return await run_service.create_run(uow, current_user.uuid, data)


@router.get("/", response_model=RunListResponse)
async def list_runs(
    current_user: CurrentUserDep,
    run_service: RunServiceDep,
    uow: UnitOfWorkDep,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    limit: Annotated[int, Query(ge=1, le=100000, description="Items per page")] = 10,
    period: Annotated[
        StatisticsPeriod | None, Query(description="Filter by time period")
    ] = None,
    min_distance: Annotated[
        float | None, Query(ge=0, description="Minimum distance")
    ] = None,
    max_distance: Annotated[
        float | None, Query(ge=0, description="Maximum distance")
    ] = None,
    sort_by: Annotated[RunSortBy, Query(description="Sort by field")] = RunSortBy.DATE,
    order: Annotated[SortOrder, Query(description="Sort order")] = SortOrder.DESC,
) -> RunListResponse:
    runs, total = await run_service.list_runs(
        uow,
        current_user.uuid,
        page=page,
        limit=limit,
        period=period,
        min_distance=min_distance,
        max_distance=max_distance,
        sort_by=sort_by,
        order=order,
    )
    total_pages = (total + limit - 1) // limit

    return RunListResponse(
        runs=runs, total=total, page=page, limit=limit, total_pages=total_pages
    )


@router.get("/{run_uuid}", response_model=RunResponse)
async def get_run(
    current_user: CurrentUserDep,
    run_uuid: UUID,
    run_service: RunServiceDep,
    uow: UnitOfWorkDep,
) -> RunResponse:
    return await run_service.get_run(uow, current_user.uuid, run_uuid)


@router.patch("/{run_uuid}", response_model=RunResponse)
async def update_run(
    current_user: CurrentUserDep,
    run_uuid: UUID,
    data: RunUpdateRequest,
    run_service: RunServiceDep,
    uow: UnitOfWorkDep,
) -> RunResponse:
    return await run_service.update_run(uow, current_user.uuid, run_uuid, data)


@router.delete("/{run_uuid}", response_model=RunResponse)
async def delete_run(
    current_user: CurrentUserDep,
    run_uuid: UUID,
    run_service: RunServiceDep,
    uow: UnitOfWorkDep,
) -> RunResponse:
    return await run_service.delete_run(uow, current_user.uuid, run_uuid)

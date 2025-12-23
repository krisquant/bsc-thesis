from fastapi import APIRouter

from app.dependencies import CurrentUserDep, StatisticsServiceDep, UnitOfWorkDep
from app.enums.statistics import StatisticsPeriod
from app.schemas.statistics import UserStatisticsResponse, VisualizationResponse

router = APIRouter()


@router.get("/", response_model=UserStatisticsResponse)
async def get_user_statistics(
    current_user: CurrentUserDep,
    statistics_service: StatisticsServiceDep,
    uow: UnitOfWorkDep,
) -> UserStatisticsResponse:
    return await statistics_service.get_user_statistics(uow, current_user.uuid)


@router.get("/visualization", response_model=VisualizationResponse)
async def get_visualization_data(
    current_user: CurrentUserDep,
    statistics_service: StatisticsServiceDep,
    uow: UnitOfWorkDep,
    period: StatisticsPeriod,
) -> VisualizationResponse:
    data = await statistics_service.get_visualization_data(
        uow, current_user.uuid, period
    )
    return VisualizationResponse(data=data)

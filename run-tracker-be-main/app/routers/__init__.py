from fastapi import APIRouter

from app.routers.achievements import router as achievements
from app.routers.auth import router as auth
from app.routers.challenge import router as challenge
from app.routers.friendships import router as friendships
from app.routers.goals import router as goals
from app.routers.health_check import router as healthcheck
from app.routers.leaderboard import router as leaderboard
from app.routers.runs import router as runs
from app.routers.statistics import router as statistics
from app.routers.users import router as users

__all__ = ["router"]

router = APIRouter(prefix="/api")

router.include_router(healthcheck, prefix="/health-check", tags=["Health Check"])
router.include_router(auth, prefix="/auth", tags=["Auth"])
router.include_router(users, prefix="/users", tags=["Users"])
router.include_router(goals, prefix="/goals", tags=["Goals"])
router.include_router(runs, prefix="/runs", tags=["Runs"])
router.include_router(achievements, prefix="/achievements", tags=["Achievements"])
router.include_router(statistics, prefix="/statistics", tags=["Statistics"])
router.include_router(leaderboard, prefix="/leaderboard", tags=["Leaderboard"])
router.include_router(friendships, prefix="/friendships", tags=["Friendships"])
router.include_router(challenge, prefix="/challenges", tags=["Challenges"])

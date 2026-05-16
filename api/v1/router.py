from fastapi import APIRouter
from api.v1.endpoints import tasks, pomodoro, auth, notification, stress_analysis, log

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(pomodoro.router, prefix="/pomodoro", tags=["pomodoro"])
api_router.include_router(notification.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(stress_analysis.router, prefix="/analysis", tags=["stress analysis"])
api_router.include_router(log.router, prefix="/logs", tags=["logs"])

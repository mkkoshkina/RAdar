from fastapi import APIRouter
from backend.api.v1.endpoints.admin import router as admin_router
from backend.api.v1.endpoints.auth import router as auth_router
from backend.api.v1.endpoints.billing import router as billing_router
from backend.api.v1.endpoints.prediction import router as predicting_router
from backend.api.v1.endpoints.chat import router as chat_router

routers = APIRouter()
router_list = [admin_router, auth_router, billing_router, predicting_router, chat_router]

for router in router_list:
    router.tags = routers.tags.append("v1")
    routers.include_router(router)

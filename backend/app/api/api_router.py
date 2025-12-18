from fastapi import APIRouter
from app.api.endpoints import seal
from app.api.endpoints import ocr

# 创建总路由
api_router = APIRouter()

api_router.include_router(seal.router, prefix="/seal", tags=["印章处理"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["智能文档识别"])

# 后面可以在这里继续注册 ocr.router ...
from fastapi import APIRouter
from app.api.endpoints import seal

# 创建总路由
api_router = APIRouter()

# 注册印章模块，前缀为 /seal
# 最终访问路径变成: http://localhost:8000/api/v1/seal/extract
api_router.include_router(seal.router, prefix="/seal", tags=["印章处理"])

# 后面可以在这里继续注册 ocr.router ...
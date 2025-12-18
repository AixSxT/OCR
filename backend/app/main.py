from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings

from app.api.api_router import api_router
# 1. 初始化 APP
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 2. 配置跨域 (CORS) - 这一步对前后端分离至关重要
# 如果没有这个，React 前端通过浏览器调用 Python 后端时会被拦截
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
# 3. 健康检查接口 (用于测试后端活没活着)
@app.get("/")
def root():
    return {
        "message": "Welcome to Smart OCR System Backend",
        "status": "running",
        "docs_url": "/docs" 
    }

# 4. 启动逻辑 (如果是直接运行此文件)
if __name__ == "__main__":
    print("🚀 正在启动后端服务...")
    # reload=True 表示你改代码后，服务器会自动重启，开发时很方便
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
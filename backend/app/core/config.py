import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 项目基础信息
    PROJECT_NAME: str = "Smart OCR System"
    API_V1_STR: str = "/api/v1"
    
    # 跨域设置 (允许前端从不同端口访问后端)
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",  # React/Vite 默认端口
        "http://localhost:3000",  # React 备用端口
        "*"                       # 调试阶段允许所有
    ]

    # --- 核心凭证 (已填入您的配置) ---
    # 您的火山引擎 API Key
    VOLC_API_KEY: str = "51db8305-18bd-4e01-bb39-9af9344ad281"
    
    # 您的 Endpoint ID (模型名称)
    VOLC_ENDPOINT_ID: str = "doubao-seed-1-6-vision-250815"
    
    # 您的 Base URL
    VOLC_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"

    class Config:
        case_sensitive = True

settings = Settings()
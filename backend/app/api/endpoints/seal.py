from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from app.services.vision_tools import vision_service

router = APIRouter()

@router.post("/extract", summary="上传图片并提取红色印章")
async def extract_seal(file: UploadFile = File(...)):
    """
    接收图片 -> 识别红色印章 -> 返回透明背景的 PNG 图片
    """
    # 1. 校验文件格式
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="仅支持 JPG 或 PNG 图片")
    
    try:
        # 2. 读取文件内容
        file_bytes = await file.read()
        
        # 3. 调用核心服务处理
        processed_image = vision_service.extract_red_seal(file_bytes)
        
        # 4. 直接返回图片流，浏览器可以直接显示
        return Response(content=processed_image, media_type="image/png")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
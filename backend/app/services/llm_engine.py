from openai import OpenAI
from app.core.config import settings
import json
import re

class LLMEngine:
    def __init__(self):
        print("🔌 正在连接火山引擎 (v6.0 全能适配模式)...")
        self.client = OpenAI(
            api_key=settings.VOLC_API_KEY,
            base_url=settings.VOLC_BASE_URL
        )

    def parse_content(self, raw_text: str) -> dict:
        """
        v6.0 Prompt：针对多店异构表格的终极适配
        新增：单位提取、DEFAULT编码处理、对钩(√)处理、手遮挡容错
        """
        
        # ⚠️ 这里的 Prompt 设计为“宽进严出”，尽可能多地捕获字段
        prompt_template = """
        # Role
        你是一个OCR数据清洗专家。你面对的是多种格式不统一的库存盘点单（如仁厚店、三合店、西安店）。

        # 核心指令 (Critical)
        1. **绝不漏行**：这是最高优先级。即使某一行没有编码（或是 DEFAULT），只要有商品名称，就必须保留！
        2. **动态列识别**：你需要根据当前图片的文字内容，判断包含哪些列。

        # 字段提取规则 (按需提取)
        请尝试从杂乱的文本中还原以下字段：
        - `store_name`: 店铺名称 (通常在开头，如"三合店")
        - `code`: 商品编码。
           - ⚠️ 注意：如果识别到 "DEFAULT" 或无编码，请保留该字段为 "DEFAULT" 或 null，**不要丢弃该行**。
        - `batch_number`: 批次/日期 (如 20250902)。仅当原文存在时输出。
        - `name`: 商品名称 (必填，这是行的主键)。
        - `spec`: 规格 (如 120g/袋, 5斤/箱)。
        - `unit`: 单位 (如 盒, 袋, 瓶, 提, 只是一个字的量词)。**如果原文有单独一列单位，请提取。**
        - `system_stock`: 系统库存/账存 (通常是印刷体的数字)。
        - `actual_count`: 实盘数量 (通常是手写体，位于最右侧)。

        # 特殊情况处理 (非常重要)
        1. **实盘数识别**：
           - 如果是数字：直接输出 (如 5, 10.5)。
           - 如果是算式：请计算结果 (如 "18+6" -> 输出 24)。
           - 如果是符号 **"✔"、"v"、"√"**：这代表【账实相符】，请将 `system_stock` 的值填入 `actual_count`。
           - 如果是 "未盘"、"/"、"-"：填 null。
        2. **列错位纠正**：OCR 可能会把 "单位" 和 "系统库存" 挤在一起（如 "盒 6"）。请利用你的常识将它们拆开："盒"是unit，"6"是system_stock。

        # Output Format
        Strictly output valid JSON only.
        {
            "status": "success",
            "data": {
                "store_name": "xxx",
                "items": [
                    {
                        "code": "PC.../DEFAULT",
                        "name": "商品名称",
                        "batch_number": "...", // 选填
                        "spec": "...",        // 选填
                        "unit": "...",        // 选填 (新增)
                        "system_stock": 10,   // 选填
                        "actual_count": 10    // 必填
                    }
                ]
            }
        }

        # Input Text
        {raw_text_placeholder}
        """

        prompt = prompt_template.replace("{raw_text_placeholder}", raw_text)

        try:
            response = self.client.chat.completions.create(
                model=settings.VOLC_ENDPOINT_ID,
                messages=[
                    {"role": "system", "content": "你是一个严谨的数据录入员。如果看到 'DEFAULT' 或空编码，必须保留该行数据。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1, 
                max_tokens=4096 
            )
            
            content = response.choices[0].message.content
            content = self._clean_json_string(content)
            return json.loads(content)
            
        except Exception as e:
            print(f"❌ LLM 处理失败: {e}")
            return {"status": "error", "message": str(e), "raw_text": raw_text}

    def _clean_json_string(self, content: str) -> str:
        content = content.replace("```json", "").replace("```", "")
        start_idx = content.find("{")
        end_idx = content.rfind("}")
        if start_idx != -1 and end_idx != -1:
            content = content[start_idx : end_idx + 1]
        return content.strip()

llm_engine = LLMEngine()
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from notdiamond_openai_adapter import create_adapter
from pydantic import BaseModel, Field
from typing import List, Optional, Union
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = FastAPI(title="NotDiamond OpenAI Adapter")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建适配器实例
adapter = create_adapter()

# OpenAI兼容的请求模型
class ChatMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: Union[str, List[str]]
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    user: Optional[str] = None

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    try:
        # 转换模型格式
        model_candidates = (
            [request.model] if isinstance(request.model, str) 
            else request.model
        )
        
        # 确保模型名称包含提供商前缀
        model_candidates = [
            m if '/' in m else f"openai/{m}" 
            for m in model_candidates
        ]
        
        # 转换消息格式
        messages = [msg.dict() for msg in request.messages]
        
        response = await adapter.route_request(
            messages=messages,
            model_candidates=model_candidates,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            presence_penalty=request.presence_penalty,
            frequency_penalty=request.frequency_penalty,
        )
        
        return JSONResponse(content=response)
    
    except Exception as e:
        error_response = {
            "error": {
                "message": str(e),
                "type": "internal_error",
                "code": "internal_error"
            }
        }
        return JSONResponse(
            status_code=500,
            content=error_response
        )

class FeedbackRequest(BaseModel):
    session_id: str
    score: float
    feedback_type: str = "quality"

@app.post("/v1/feedback")
async def submit_feedback(request: FeedbackRequest):
    try:
        adapter.submit_feedback(
            session_id=request.session_id,
            score=request.score,
            feedback_type=request.feedback_type
        )
        return {"status": "success"}
    except Exception as e:
        error_response = {
            "error": {
                "message": str(e),
                "type": "feedback_error",
                "code": "feedback_error"
            }
        }
        return JSONResponse(
            status_code=500,
            content=error_response
        ) 
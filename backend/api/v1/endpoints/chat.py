from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Echo the user's message back
    return ChatResponse(reply=request.message)
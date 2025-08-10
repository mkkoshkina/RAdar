# RAdar-SNP2Risk-RA/backend/api/v1/endpoints/chatbot.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chatbot",
    tags=["chatbot"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str

# Get the agent API URL from environment variable
AGENT_API_URL = os.environ.get("AGENT_API_URL", "http://176.108.244.85:8888")

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info(f"Attempting to connect to agent API at: {AGENT_API_URL}")
    logger.info(f"Request data: session_id={request.session_id}, message='{request.message[:50]}...'")
    
    try:
        # Increase timeout significantly for slow agent responses
        timeout_config = httpx.Timeout(
            connect=10.0,    # 10 seconds to establish connection
            read=300.0,      # 5 minutes to read response (very slow agents)
            write=10.0,      # 10 seconds to send request
            pool=10.0        # 10 seconds to get connection from pool
        )
        
        async with httpx.AsyncClient(timeout=timeout_config) as client:
            logger.info(f"Making POST request to {AGENT_API_URL}/query with extended timeout")
            
            agent_response = await client.post(
                f"{AGENT_API_URL}/query",
                json={"session_id": request.session_id, "message": request.message},
                headers={"Content-Type": "application/json"}
            )
            
            logger.info(f"Response status: {agent_response.status_code}")
            
            agent_response.raise_for_status()
            response_data = agent_response.json()
            logger.info(f"Response data received: {len(response_data.get('reply', ''))} characters")
            
            reply = response_data["reply"]
            return ChatResponse(response=reply)
            
    except httpx.ConnectError as e:
        error_msg = f"Connection error to agent API: {e}"
        logger.error(error_msg)
        return ChatResponse(response=f"Connection failed: {error_msg}")
        
    except httpx.TimeoutException as e:
        error_msg = f"Agent API is taking longer than 5 minutes to respond. This might indicate the agent is processing a complex request."
        logger.error(f"Timeout connecting to agent API: {e}")
        return ChatResponse(response=error_msg)
        
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error from agent API: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return ChatResponse(response=f"API error: {error_msg}")
        
    except KeyError as e:
        error_msg = f"Missing key in response: {e}"
        logger.error(error_msg)
        return ChatResponse(response=f"Invalid response format: {error_msg}")
        
    except Exception as e:
        error_msg = f"Unexpected error connecting to agent API: {type(e).__name__}: {e}"
        logger.error(error_msg)
        return ChatResponse(response=f"Unexpected error: {error_msg}")

@router.post("/end_chat")
async def end_chat(request: ChatRequest):
    try:
        timeout_config = httpx.Timeout(connect=5.0, read=30.0, write=5.0, pool=5.0)
        async with httpx.AsyncClient(timeout=timeout_config) as client:
            await client.post(
                f"{AGENT_API_URL}/end_session",
                params={"session_id": request.session_id}
            )
        return {"status": "Session closed"}
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return {"status": "Error closing session"}

# Add a health check endpoint
@router.get("/health")
async def health_check():
    try:
        timeout_config = httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)
        async with httpx.AsyncClient(timeout=timeout_config) as client:
            # Try to reach the agent API
            response = await client.get(f"{AGENT_API_URL}/")
            return {
                "status": "healthy",
                "agent_api_url": AGENT_API_URL,
                "agent_api_reachable": response.status_code < 400
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "agent_api_url": AGENT_API_URL,
            "agent_api_reachable": False,
            "error": str(e)
        }
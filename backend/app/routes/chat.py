from fastapi import APIRouter
from app.schemas.chat import ChatRequest
from app.services.llm import client
from app.services.agent_loop import run_agent

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.post("/")
async def chat(data: ChatRequest):
    
    if len(data.prompt) < 3:
        return {
            "error": "write your prompt clearly."
        }
        
    completion = run_agent(data.prompt)
    
    return {
        "response": completion.choices[0].message.content    
    }

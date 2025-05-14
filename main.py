from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
from agent_module import CustomerSupportAgent
import uuid
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Initialize FastAPI app
app = FastAPI(title="Customer Support Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Store active conversations
active_agents: Dict[str, CustomerSupportAgent] = {}

# Initialize the database with sample data
@app.on_event("startup")
async def startup_event():
    # Create a temporary agent to initialize the database
    temp_agent = CustomerSupportAgent()
    temp_agent.db.initialize_sample_data()
    temp_agent.close()
    print("Application started and database initialized with sample data")

# Models for request and response
class MessageRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class MessageResponse(BaseModel):
    conversation_id: str
    response: str

class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    messages: List[Dict[str, str]]

# Endpoints
@app.post("/message", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    """Process a user message and return the agent's response"""
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Get or create agent for this conversation
    if conversation_id not in active_agents:
        active_agents[conversation_id] = CustomerSupportAgent(conversation_id)
    
    # Process the message
    response = active_agents[conversation_id].process_user_message(request.message)
    
    return MessageResponse(
        conversation_id=conversation_id,
        response=response
    )

@app.get("/conversation/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation(conversation_id: str):
    """Get the conversation history for a specific ID"""
    if conversation_id not in active_agents:
        active_agents[conversation_id] = CustomerSupportAgent(conversation_id)
    
    history = active_agents[conversation_id].memory.get_conversation_history()
    
    return ConversationHistoryResponse(
        conversation_id=conversation_id,
        messages=history
    )

@app.delete("/conversation/{conversation_id}")
async def reset_conversation(conversation_id: str):
    """Reset a conversation"""
    if conversation_id in active_agents:
        active_agents[conversation_id].reset_conversation()
        return {"status": "success", "message": f"Conversation {conversation_id} reset"}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

@app.on_event("shutdown")
async def shutdown_event():
    """Close all database connections when shutting down"""
    for agent in active_agents.values():
        agent.close()
    print("Application shutting down, all connections closed")

# Run the app
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
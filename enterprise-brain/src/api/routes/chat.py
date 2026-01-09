from fastapi import APIRouter, HTTPException
from src.api.schemas import ChatRequest, ChatResponse
from src.core.agent import build_agent
from src.core.llm import get_embeddings
from src.core.memory import get_checkpointer
from langchain_core.messages import HumanMessage
import uuid

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        embeddings = get_embeddings()
        checkpointer = get_checkpointer()
        
        # Build agent with memory
        graph, _ = build_agent(pro_mode=request.pro_mode, embeddings=embeddings, checkpointer=checkpointer)
        
        # Setup config with thread_id
        session_id = request.session_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": session_id}}
        
        # Invoke the graph
        inputs = {"messages": [HumanMessage(content=request.message)]}
        result = graph.invoke(inputs, config=config)
        
        # Extract the last message content
        last_message = result["messages"][-1]
        response_text = last_message.content
        
        # Extract sources from ToolMessages
        sources = set()
        for msg in result["messages"]:
            if msg.type == "tool" and msg.name == "knowledge_base":
                # Parse "Source: filename" lines
                lines = msg.content.split('\n')
                for line in lines:
                    if line.startswith("Source: "):
                        sources.add(line.replace("Source: ", "").strip())
        
        return ChatResponse(response=response_text, sources=list(sources))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

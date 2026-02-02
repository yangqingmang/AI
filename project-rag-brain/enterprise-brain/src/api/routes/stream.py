from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from src.api.schemas import ChatRequest
from src.core.agent import build_agent
from src.core.llm import get_embeddings
from src.core.memory import get_checkpointer
from langchain_core.messages import HumanMessage
import json
import asyncio
import uuid

router = APIRouter()

async def event_generator(message: str, pro_mode: bool, session_id: str = None):
    """
    Generator function for SSE.
    Yields JSON strings formatted as SSE events.
    """
    try:
        embeddings = get_embeddings()
        checkpointer = get_checkpointer()
        
        graph, _ = build_agent(pro_mode=pro_mode, embeddings=embeddings, checkpointer=checkpointer)
        
        # Setup config
        thread_id = session_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        inputs = {"messages": [HumanMessage(content=message)]}
        
        # Use astream_events to get granular token-by-token updates
        # version="v2" is standard for newer LangChain versions
        async for event in graph.astream_events(inputs, config=config, version="v2"):
            kind = event["event"]
            
            # Filter for LLM streaming events to get tokens
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    # Construct a JSON data payload
                    payload = json.dumps({"token": content})
                    yield f"data: {payload}\n\n"
            
            # Handle Tool Start (Thinking Process)
            elif kind == "on_tool_start":
                tool_name = event["name"]
                # We can also get input args if we want to show what it's searching for
                tool_input = event["data"].get("input")
                payload = json.dumps({"tool_start": tool_name, "input": tool_input})
                yield f"data: {payload}\n\n"

            # Handle Tool Output for Sources
            elif kind == "on_tool_end" and event["name"] == "knowledge_base":
                tool_output = event["data"].get("output")
                if tool_output and isinstance(tool_output, str):
                    lines = tool_output.split('\n')
                    for line in lines:
                        if line.startswith("Source: "):
                            source_name = line.replace("Source: ", "").strip()
                            payload = json.dumps({"source": source_name})
                            yield f"data: {payload}\n\n"
                
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        error_payload = json.dumps({"error": str(e)})
        yield f"data: {error_payload}\n\n"

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat response using Server-Sent Events (SSE).
    """
    return StreamingResponse(
        event_generator(request.message, request.pro_mode, request.session_id),
        media_type="text/event-stream"
    )

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import os
import sys

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("src.api.routes.chat.build_agent")
@patch("src.api.routes.chat.get_embeddings")
@patch("src.api.routes.chat.get_checkpointer")
def test_chat_endpoint(mock_get_checkpointer, mock_get_embeddings, mock_build_agent):
    # Mock embeddings
    mock_get_embeddings.return_value = MagicMock()
    mock_get_checkpointer.return_value = MagicMock()
    
    # Mock agent graph
    mock_graph = MagicMock()
    # Simulate the structure of the last message
    mock_message = MagicMock()
    mock_message.content = "Hello! I am the Brain."
    
    mock_graph.invoke.return_value = {
        "messages": [mock_message]
    }
    mock_build_agent.return_value = (mock_graph, "System Prompt")

    response = client.post("/api/v1/chat", json={"message": "Hello", "session_id": "test-session"})
    
    assert response.status_code == 200
    assert response.json()["response"] == "Hello! I am the Brain."

@patch("src.api.routes.stream.build_agent")
@patch("src.api.routes.stream.get_embeddings")
@patch("src.api.routes.stream.get_checkpointer")
def test_chat_stream_endpoint(mock_get_checkpointer, mock_get_embeddings, mock_build_agent):
    # Mock embeddings
    mock_get_embeddings.return_value = MagicMock()
    mock_get_checkpointer.return_value = MagicMock()
    
    # Mock agent graph with astream_events
    mock_graph = MagicMock()
    
    # Correctly mock an async generator
    async def async_gen(*args, **kwargs):
        yield {"event": "on_chat_model_stream", "data": {"chunk": MagicMock(content="Hello")}}
        yield {"event": "on_chat_model_stream", "data": {"chunk": MagicMock(content=" World")}}
        # Mock source event
        yield {"event": "on_tool_end", "name": "knowledge_base", "data": {"output": "Source: doc1.pdf\nContent: ..."}}
    
    # Assign the async generator function to the side_effect, NOT an AsyncMock
    # Because astream_events is called as a method, we need to ensure it returns the generator
    mock_graph.astream_events.side_effect = async_gen
    
    mock_build_agent.return_value = (mock_graph, "System Prompt")

    with client.stream("POST", "/api/v1/chat/stream", json={"message": "Hi", "session_id": "test-stream"}) as response:
        assert response.status_code == 200
        # Iterate lines (TestClient.stream iter_lines can return strings)
        lines = list(response.iter_lines())
        
        # Check for SSE format "data: ..."
        assert any("Hello" in line for line in lines)
        assert any("World" in line for line in lines)
        # Check for source
        assert any("doc1.pdf" in line for line in lines)
        assert any("[DONE]" in line for line in lines)

@patch("src.api.routes.upload.glob.glob")
@patch("src.api.routes.upload.os.path.exists")
def test_list_files(mock_exists, mock_glob):
    mock_exists.return_value = True
    # Mock glob to return some files
    # glob is called multiple times for different extensions
    # side_effect can be a list of return values
    mock_glob.side_effect = [
        ["/data/doc1.pdf"], # pdf
        ["/data/doc2.txt"], # txt
        ["/data/doc3.md"]   # md
    ]
    
    response = client.get("/api/v1/files")
    assert response.status_code == 200
    files = response.json()
    assert "doc1.pdf" in files
    assert "doc2.txt" in files
    assert "doc3.md" in files
    assert len(files) == 3

@patch("src.api.routes.upload.ingest_docs")
@patch("src.api.routes.upload.shutil.copyfileobj")
def test_upload_endpoint(mock_copy, mock_ingest):
    # Mock file upload
    filename = "test_doc.txt"
    file_content = b"Dummy content"
    
    files = {"file": (filename, file_content, "text/plain")}
    
    response = client.post("/api/v1/upload", files=files)
    
    assert response.status_code == 200
    assert response.json()["filename"] == filename
    assert "triggered" in response.json()["status"]

import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.retriever import get_retriever, reset_bm25_cache
from unittest.mock import MagicMock, patch

@patch("src.core.retriever.load_all_docs")
@patch("src.core.retriever.DBFactory")
@patch("src.core.retriever.EnsembleRetriever")
def test_hybrid_retriever(mock_ensemble, mock_db_factory, mock_load_docs):
    # Setup Mocks
    mock_embeddings = MagicMock()
    
    # Mock Vector Store
    mock_vector_store = MagicMock()
    mock_vector_retriever = MagicMock()
    mock_vector_store.as_retriever.return_value = mock_vector_retriever
    mock_db_factory.get_vector_store.return_value = mock_vector_store
    
    # Mock Documents for BM25
    mock_doc = MagicMock()
    mock_doc.page_content = "Test content"
    mock_load_docs.return_value = [mock_doc]
    
    # Test initialization
    reset_bm25_cache()
    retriever = get_retriever(mock_embeddings)
    
    # Verify EnsembleRetriever was called
    mock_ensemble.assert_called_once()
    
    # Check arguments passed to EnsembleRetriever
    call_args = mock_ensemble.call_args[1]
    retrievers = call_args['retrievers']
    weights = call_args['weights']
    
    assert len(retrievers) == 2
    assert retrievers[1] == mock_vector_retriever  # 2nd is vector
    assert weights == [0.4, 0.6]

@patch("src.core.retriever.load_all_docs")
@patch("src.core.retriever.DBFactory")
def test_hybrid_retriever_fallback(mock_db_factory, mock_load_docs):
    """Test fallback to vector only if no docs found"""
    mock_embeddings = MagicMock()
    
    mock_vector_store = MagicMock()
    mock_vector_retriever = MagicMock()
    mock_vector_store.as_retriever.return_value = mock_vector_retriever
    mock_db_factory.get_vector_store.return_value = mock_vector_store
    
    # Empty docs
    mock_load_docs.return_value = []
    
    reset_bm25_cache()
    retriever = get_retriever(mock_embeddings)
    
    # Should return vector retriever directly
    assert retriever == mock_vector_retriever

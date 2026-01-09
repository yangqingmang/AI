import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
import os
from src.config.settings import get_settings

settings = get_settings()
_checkpointer = None

def get_checkpointer():
    """
    Returns a singleton SqliteSaver instance.
    """
    global _checkpointer
    if _checkpointer is None:
        db_path = os.path.join(settings.BASE_DIR, "chat_history.db")
        conn = sqlite3.connect(db_path, check_same_thread=False)
        _checkpointer = SqliteSaver(conn)
    return _checkpointer

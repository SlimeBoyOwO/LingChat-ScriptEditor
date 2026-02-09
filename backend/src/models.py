from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Union

# --- Configuration Models ---
class ScriptSettings(BaseModel):
    user_name: Optional[str] = None
    user_subtitle: Optional[str] = None

class ScriptConfig(BaseModel):
    id: Optional[str] = None
    script_name: str
    intro_charpter: str
    description: Optional[str] = None
    script_settings: Optional[ScriptSettings] = None

# --- Chapter/Event Models ---

class Event(BaseModel):
    type: str
    duration: float = 0
    condition: Optional[str] = None
    isFinal: Optional[bool] = None
    
    # Capture all other fields
    class Config:
        extra = "allow"

class Chapter(BaseModel):
    events: List[Union[Event, Dict[str, Any]]] 

class CreateScriptRequest(BaseModel):
    name: str
    description: str
    user_name: str
    user_subtitle: str
    intro_chapter: str

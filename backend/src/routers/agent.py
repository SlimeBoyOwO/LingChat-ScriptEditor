"""
AI Agent Router for Script Editor
Provides API endpoints for AI-powered script writing assistance
"""
import json
import os
import yaml
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..services.ai_service import ai_service

# Scripts base path
SCRIPTS_BASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scripts")

router = APIRouter(
    prefix="/api/agent",
    tags=["agent"]
)

# --- Models ---

class AgentConfigRequest(BaseModel):
    api_key: str
    api_base: Optional[str] = "https://api.openai.com/v1"
    model: Optional[str] = "gpt-4o-mini"

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    script_id: str
    chapter_path: str
    chapter_content: Dict[str, Any]  # Current chapter data
    characters: List[str]  # Available characters
    assets: Dict[str, List[str]]  # Available assets

class ChatStreamRequest(BaseModel):
    messages: List[ChatMessage]
    script_id: str
    chapter_path: str
    chapter_content: Dict[str, Any]
    characters: List[str]
    assets: Dict[str, List[str]]

# --- State Management ---
# Store modified chapter content for each session
# In production, this should be stored in a proper database
_session_state: Dict[str, Dict[str, Any]] = {}

def get_session_key(script_id: str, chapter_path: str) -> str:
    return f"{script_id}:{chapter_path}"

def get_current_chapter_content(request: ChatRequest) -> Dict[str, Any]:
    """Get the current chapter content, considering any pending modifications"""
    key = get_session_key(request.script_id, request.chapter_path)
    if key in _session_state:
        return _session_state[key]
    return request.chapter_content

def set_current_chapter_content(script_id: str, chapter_path: str, content: Dict[str, Any]):
    """Update the current chapter content"""
    key = get_session_key(script_id, chapter_path)
    _session_state[key] = content

def save_chapter_to_yaml(script_id: str, chapter_path: str, content: Dict[str, Any]) -> bool:
    """Save chapter content to YAML file"""
    try:
        # Construct the full file path
        file_path = os.path.join(SCRIPTS_BASE_PATH, script_id, chapter_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write to YAML file
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(content, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        print(f"[DEBUG] Saved chapter to: {file_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save chapter: {e}")
        return False

# --- Tool Handlers ---

async def handle_list_characters(characters: List[str], **kwargs) -> Dict[str, Any]:
    """Return the list of available characters"""
    print(f"[DEBUG] handle_list_characters called with characters: {characters}")
    return {
        "success": True,
        "characters": characters,
        "count": len(characters)
    }

async def handle_list_assets(assets: Dict[str, List[str]], category: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Return the list of available assets"""
    if category and category in assets:
        return {
            "success": True,
            "category": category,
            "assets": assets[category]
        }
    return {
        "success": True,
        "assets": assets
    }

async def handle_get_chapter(chapter_content: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Return the current chapter content"""
    return {
        "success": True,
        "chapter": chapter_content
    }

async def handle_append_event(event: Dict[str, Any], chapter_content: Dict[str, Any], script_id: str, chapter_path: str, **kwargs) -> Dict[str, Any]:
    """Append an event to the chapter"""
    if "events" not in chapter_content:
        chapter_content["events"] = []
    
    chapter_content["events"].append(event)
    set_current_chapter_content(script_id, chapter_path, chapter_content)
    
    # Save to YAML file
    save_success = save_chapter_to_yaml(script_id, chapter_path, chapter_content)
    
    return {
        "success": save_success,
        "message": f"Added event of type '{event.get('type')}' at position {len(chapter_content['events']) - 1}",
        "total_events": len(chapter_content["events"]),
        "saved_to_file": save_success
    }

async def handle_insert_event(index: int, event: Dict[str, Any], chapter_content: Dict[str, Any], script_id: str, chapter_path: str, **kwargs) -> Dict[str, Any]:
    """Insert an event at a specific position"""
    if "events" not in chapter_content:
        chapter_content["events"] = []
    
    if index < 0 or index > len(chapter_content["events"]):
        return {
            "success": False,
            "error": f"Invalid index {index}. Chapter has {len(chapter_content['events'])} events."
        }
    
    chapter_content["events"].insert(index, event)
    set_current_chapter_content(script_id, chapter_path, chapter_content)
    
    # Save to YAML file
    save_success = save_chapter_to_yaml(script_id, chapter_path, chapter_content)
    
    return {
        "success": save_success,
        "message": f"Inserted event of type '{event.get('type')}' at position {index}",
        "index": index,
        "total_events": len(chapter_content["events"]),
        "saved_to_file": save_success
    }

async def handle_update_event(index: int, event: Dict[str, Any], chapter_content: Dict[str, Any], script_id: str, chapter_path: str, **kwargs) -> Dict[str, Any]:
    """Update an event at a specific position"""
    if "events" not in chapter_content or index < 0 or index >= len(chapter_content["events"]):
        return {
            "success": False,
            "error": f"Invalid index {index}. Chapter has {len(chapter_content.get('events', []))} events."
        }
    
    chapter_content["events"][index] = event
    set_current_chapter_content(script_id, chapter_path, chapter_content)
    
    # Save to YAML file
    save_success = save_chapter_to_yaml(script_id, chapter_path, chapter_content)
    
    return {
        "success": save_success,
        "message": f"Updated event at position {index}",
        "index": index,
        "total_events": len(chapter_content["events"]),
        "saved_to_file": save_success
    }

async def handle_delete_event(index: int, chapter_content: Dict[str, Any], script_id: str, chapter_path: str, **kwargs) -> Dict[str, Any]:
    """Delete an event at a specific position"""
    if "events" not in chapter_content or index < 0 or index >= len(chapter_content["events"]):
        return {
            "success": False,
            "error": f"Invalid index {index}. Chapter has {len(chapter_content.get('events', []))} events."
        }
    
    deleted_event = chapter_content["events"].pop(index)
    set_current_chapter_content(script_id, chapter_path, chapter_content)
    
    # Save to YAML file
    save_success = save_chapter_to_yaml(script_id, chapter_path, chapter_content)
    
    return {
        "success": save_success,
        "message": f"Deleted event of type '{deleted_event.get('type')}' at position {index}",
        "deleted_index": index,
        "deleted_event_type": deleted_event.get('type'),
        "total_events": len(chapter_content["events"]),
        "saved_to_file": save_success
    }


def create_tool_handlers(request_data: ChatRequest) -> Dict[str, Any]:
    """Create tool handlers with access to request context"""
    current_content = get_current_chapter_content(request_data)
    
    async def list_characters(**kwargs):
        return await handle_list_characters(request_data.characters, **kwargs)
    
    async def list_assets(**kwargs):
        return await handle_list_assets(request_data.assets, **kwargs)
    
    async def get_chapter(**kwargs):
        return await handle_get_chapter(current_content, **kwargs)
    
    async def append_event(**kwargs):
        return await handle_append_event(
            event=kwargs.get("event"),
            chapter_content=current_content,
            script_id=request_data.script_id,
            chapter_path=request_data.chapter_path
        )
    
    async def insert_event(**kwargs):
        return await handle_insert_event(
            index=kwargs.get("index"),
            event=kwargs.get("event"),
            chapter_content=current_content,
            script_id=request_data.script_id,
            chapter_path=request_data.chapter_path
        )
    
    async def update_event(**kwargs):
        return await handle_update_event(
            index=kwargs.get("index"),
            event=kwargs.get("event"),
            chapter_content=current_content,
            script_id=request_data.script_id,
            chapter_path=request_data.chapter_path
        )
    
    async def delete_event(**kwargs):
        return await handle_delete_event(
            index=kwargs.get("index"),
            chapter_content=current_content,
            script_id=request_data.script_id,
            chapter_path=request_data.chapter_path
        )
    
    return {
        "list_characters": list_characters,
        "list_assets": list_assets,
        "get_chapter": get_chapter,
        "append_event": append_event,
        "insert_event": insert_event,
        "update_event": update_event,
        "delete_event": delete_event
    }


# --- Routes ---

@router.post("/config")
async def set_agent_config(config: AgentConfigRequest):
    """Set the AI agent configuration (API key, base URL, model)"""
    try:
        ai_service.set_config(
            api_key=config.api_key,
            api_base=config.api_base or "https://api.openai.com/v1",
            model=config.model or "gpt-4o-mini"
        )
        return {"success": True, "message": "Configuration saved", "model": config.model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_agent_config():
    """Get the current AI agent configuration (without API key)"""
    return {
        "configured": ai_service.is_configured(),
        "api_base": ai_service.config.api_base,
        "model": ai_service.config.model
    }


@router.post("/chat")
async def chat(request: ChatRequest):
    """Send a message to the AI agent and get a response"""
    if not ai_service.is_configured():
        raise HTTPException(status_code=400, detail="API key not configured. Please set your OpenAI API key first.")
    
    try:
        # Debug logging
        print(f"[DEBUG] Chat request - script_id: {request.script_id}, chapter_path: {request.chapter_path}")
        print(f"[DEBUG] Characters: {request.characters}")
        print(f"[DEBUG] Chapter content type: {type(request.chapter_content)}")
        
        # Convert messages to the format expected by ai_service
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        # Create tool handlers with context
        tool_handlers = create_tool_handlers(request)
        
        # Call AI service
        result = await ai_service.chat(messages, tool_handlers)
        
        if result.get("error"):
            print(f"[DEBUG] AI service error: {result['error']}")
            return {
                "success": False,
                "error": result["error"],
                "content": None,
                "modified_chapter": get_current_chapter_content(request)
            }
        
        return {
            "success": True,
            "content": result.get("content"),
            "tool_results": result.get("tool_results", []),
            "modified_chapter": get_current_chapter_content(request)
        }
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Chat endpoint error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatStreamRequest):
    """Send a message to the AI agent and get a streaming response"""
    if not ai_service.is_configured():
        raise HTTPException(status_code=400, detail="API key not configured. Please set your OpenAI API key first.")
    
    async def generate():
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        tool_handlers = create_tool_handlers(request)
        
        async for chunk in ai_service.chat_stream(messages, tool_handlers):
            # Include modified chapter in tool_result chunks
            if chunk["type"] == "tool_result" or chunk["type"] == "tool_error":
                chunk["modified_chapter"] = get_current_chapter_content(request)
            
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        
        # Send final modified chapter
        final_content = get_current_chapter_content(request)
        yield f"data: {json.dumps({'type': 'done', 'modified_chapter': final_content}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/reset")
async def reset_session(script_id: str, chapter_path: str):
    """Reset the session state for a chapter (discard AI modifications)"""
    key = get_session_key(script_id, chapter_path)
    if key in _session_state:
        del _session_state[key]
        return {"success": True, "message": "Session reset"}
    return {"success": True, "message": "No session to reset"}


@router.get("/events/schema")
async def get_event_schema():
    """Get the schema for supported event types"""
    return {
        "event_types": {
            "narration": {
                "description": "叙述文本",
                "required": ["text"],
                "fields": {
                    "text": {"type": "string", "description": "叙述内容"},
                    "condition": {"type": "string", "description": "变量条件表达式"},
                    "duration": {"type": "number", "description": "持续时间"}
                }
            },
            "player": {
                "description": "玩家说话",
                "required": ["text"],
                "fields": {
                    "text": {"type": "string", "description": "玩家说的话"},
                    "condition": {"type": "string", "description": "变量条件表达式"},
                    "duration": {"type": "number", "description": "持续时间"}
                }
            },
            "dialogue": {
                "description": "角色对话",
                "required": ["character", "text"],
                "fields": {
                    "character": {"type": "string", "description": "角色名称"},
                    "text": {"type": "string", "description": "对话内容"},
                    "condition": {"type": "string", "description": "变量条件表达式"},
                    "duration": {"type": "number", "description": "持续时间"}
                }
            },
            "ai_dialogue": {
                "description": "AI对话（由AI生成的动态对话）",
                "required": ["character", "prompt"],
                "fields": {
                    "character": {"type": "string", "description": "角色名称"},
                    "prompt": {"type": "string", "description": "给AI的提示"},
                    "condition": {"type": "string", "description": "变量条件表达式"},
                    "duration": {"type": "number", "description": "持续时间"}
                }
            },
            "modify_character": {
                "description": "修改角色（显示/隐藏/移动) 如果当前章节有角色事件但没有show_character的action，需要先显示角色",
                "required": ["action", "character"],
                "fields": {
                    "action": {"type": "string", "enum": ["show_character", "hide_character", "move_character", "shake_character"], "description": "操作类型"},
                    "character": {"type": "string", "description": "角色名称"},
                    "emotion": {"type": "string", "description": "表情"},
                    "condition": {"type": "string", "description": "变量条件表达式"},
                    "duration": {"type": "number", "description": "持续时间"}
                }
            },
            "background": {
                "description": "设置背景图片",
                "required": ["imagePath"],
                "fields": {
                    "imagePath": {"type": "string", "description": "背景图片路径"},
                    "condition": {"type": "string", "description": "变量条件表达式"},
                    "duration": {"type": "number", "description": "持续时间"}
                }
            },
            "music": {
                "description": "播放背景音乐",
                "required": ["musicPath"],
                "fields": {
                    "musicPath": {"type": "string", "description": "音乐文件路径"},
                    "condition": {"type": "string", "description": "变量条件表达式"},
                    "duration": {"type": "number", "description": "持续时间"}
                }
            },
            "input": {
                "description": "玩家输入事件",
                "required": ["hint"],
                "fields": {
                    "hint": {"type": "string", "description": "输入提示文字"},
                    "condition": {"type": "string", "description": "变量条件表达式"},
                    "duration": {"type": "number", "description": "持续时间"}
                }
            },
            "choices": {
                "description": "玩家选择事件",
                "required": ["options", "allow_free"],
                "fields": {
                    "options": {"type": "string", "description": "选项列表"},
                    "allow_free": {"type": "boolean", "description": "是否允许自由输入"},
                    "condition": {"type": "string", "description": "变量条件表达式"},
                    "duration": {"type": "number", "description": "持续时间"}
                }
            },
            "set_variable": {
                "description": "设置变量值",
                "required": ["name", "value"],
                "fields": {
                    "name": {"type": "string", "description": "变量名"},
                    "value": {"type": "any", "description": "变量值"},
                    "condition": {"type": "string", "description": "变量条件表达式"},
                    "duration": {"type": "number", "description": "持续时间"}
                }
            },
            "chapter_end": {
                "description": "章节结束/跳转",
                "required": ["end_type", "next_chapter"],
                "fields": {
                    "end_type": {"type": "string", "enum": ["linear", "branching", "ai_judged"], "description": "结束类型"},
                    "next_chapter": {"type": "string", "description": "下一章节路径或'end'"},
                    "options": {"type": "string", "description": "用于branching/ai_judged的选项列表"},
                    "condition": {"type": "string", "description": "变量条件表达式"},
                    "duration": {"type": "number", "description": "持续时间"}
                }
            }
        }
    }

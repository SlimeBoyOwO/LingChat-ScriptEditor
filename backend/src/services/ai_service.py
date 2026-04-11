"""
AI Service for Script Editor Agent
Handles OpenAI API calls with Function Calling for script editing tools
"""
import json
import httpx
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class AgentConfig:
    api_key: str = ""
    api_base: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"


# System prompt for the script writing agent
SYSTEM_PROMPT = """你是一个专业的视觉小说/剧情游戏剧本写作助手。你帮助用户创建和编辑剧本事件。

你可以调用以下工具来操作剧本：

1. list_characters - 获取当前剧本中可用的角色列表
2. list_assets - 获取当前剧本中的资源（背景图片、音乐、音效）
3. get_chapter - 获取当前章节的内容
4. append_event - 在章节末尾添加一个事件
5. insert_event - 在指定位置插入事件
6. update_event - 更新某个事件
7. delete_event - 删除某个事件

事件类型包括：

1. narration - 叙述文本
   必需字段: text (叙述内容)
   可选字段: condition (变量条件表达式), duration (持续时间)

2. player - 玩家说话
   必需字段: text (玩家说的话)
   可选字段: condition, duration

3. dialogue - 角色对话
   必需字段: character (角色名称), text (对话内容)
   可选字段: condition, duration

4. ai_dialogue - AI对话（由AI动态生成的对话）
   必需字段: character (角色名称), prompt (给AI的提示)
   可选字段: condition, duration

5. modify_character - 修改角色状态
   必需字段: action (show_character/hide_character/move_character/shake_character), character (角色名称)
   可选字段: emotion (表情), condition, duration

6. background - 设置背景图片
   必需字段: imagePath (背景图片路径)
   可选字段: condition, duration

7. music - 播放背景音乐
   必需字段: musicPath (音乐文件路径)
   可选字段: condition, duration

8. input - 玩家输入事件
   必需字段: hint (输入提示文字)
   可选字段: condition, duration

9. choices - 玩家选择事件
   必需字段: options (选项列表), allow_free (是否允许自由输入，默认false)
   可选字段: condition, duration

10. set_variable - 设置变量值
    必需字段: name (变量名), value (变量值)
    可选字段: condition, duration

11. chapter_end - 章节结束/跳转
    必需字段: end_type (linear/branching/ai_judged), next_chapter (下一章节路径或"end")
    可选字段: options (用于branching/ai_judged的选项列表), condition, duration

当用户要求你写剧本时，请调用相应的工具来创建事件。
请用中文回复用户。"""


# OpenAI Function definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_characters",
            "description": "获取当前剧本中可用的角色列表",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_assets",
            "description": "获取当前剧本中的资源列表（背景图片、音乐、音效等）",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "资源类别: Backgrounds, Musics, Sounds, 或留空获取全部"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_chapter",
            "description": "获取当前章节的内容",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "append_event",
            "description": "在章节末尾添加一个事件",
            "parameters": {
                "type": "object",
                "properties": {
                    "event": {
                        "type": "object",
                        "description": "事件对象，必须包含 type 字段"
                    }
                },
                "required": ["event"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "insert_event",
            "description": "在指定位置插入一个事件",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "插入位置（0-based索引）"
                    },
                    "event": {
                        "type": "object",
                        "description": "事件对象，必须包含 type 字段"
                    }
                },
                "required": ["index", "event"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_event",
            "description": "更新指定位置的事件",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "事件位置（0-based索引）"
                    },
                    "event": {
                        "type": "object",
                        "description": "新的事件对象"
                    }
                },
                "required": ["index", "event"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_event",
            "description": "删除指定位置的事件",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "事件位置（0-based索引）"
                    }
                },
                "required": ["index"]
            }
        }
    }
]


class AIService:
    def __init__(self):
        self.config = AgentConfig()
    
    def set_config(self, api_key: str, api_base: str = "https://api.openai.com/v1", model: str = "gpt-4o-mini"):
        self.config.api_key = api_key
        # Normalize the API base URL
        base = api_base.strip().rstrip("/")
        
        # Ensure URL has protocol
        if not base.startswith("http://") and not base.startswith("https://"):
            base = "https://" + base
        
        # Remove /chat/completions if present (we'll add it later)
        if base.endswith("/chat/completions"):
            base = base[:-len("/chat/completions")]
        
        self.config.api_base = base
        self.config.model = model
        print(f"[DEBUG] AI Service configured - API Base: {self.config.api_base}, Model: {self.config.model}")
    
    def is_configured(self) -> bool:
        return bool(self.config.api_key)
    
    def _get_chat_url(self) -> str:
        """Get the full chat completions URL"""
        return f"{self.config.api_base}/chat/completions"
    
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tool_handlers: Dict[str, Callable]
    ) -> Dict[str, Any]:
        """
        Send a chat request to OpenAI API and handle tool calls
        
        Args:
            messages: Chat history
            tool_handlers: Dict mapping tool names to handler functions
        
        Returns:
            Response with content and tool results
        """
        if not self.is_configured():
            return {"error": "API key not configured", "content": None}
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                *messages
            ],
            "tools": TOOLS,
            "tool_choice": "auto"
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.config.api_base}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    return {"error": f"API error: {response.status_code} - {error_text}", "content": None}
                
                data = response.json()
                choice = data["choices"][0]
                message = choice["message"]
                
                # Check if there are tool calls - use a loop to handle multiple rounds
                all_tool_results = []
                current_messages = list(messages)
                current_message = message
                max_iterations = 10  # Prevent infinite loops
                iteration = 0
                
                while current_message.get("tool_calls") and iteration < max_iterations:
                    iteration += 1
                    tool_results = []
                    
                    for tool_call in current_message["tool_calls"]:
                        function_name = tool_call["function"]["name"]
                        # Handle potential JSON parsing issues
                        try:
                            function_args = json.loads(tool_call["function"]["arguments"])
                        except json.JSONDecodeError as e:
                            print(f"[DEBUG] JSON decode error for {function_name}: {e}")
                            print(f"[DEBUG] Raw arguments: {tool_call['function']['arguments']}")
                            function_args = {}
                        
                        # Execute the tool
                        if function_name in tool_handlers:
                            try:
                                result = await tool_handlers[function_name](**function_args)
                                tool_results.append({
                                    "tool_call_id": tool_call["id"],
                                    "function_name": function_name,
                                    "result": result
                                })
                            except Exception as e:
                                tool_results.append({
                                    "tool_call_id": tool_call["id"],
                                    "function_name": function_name,
                                    "error": str(e)
                                })
                        else:
                            tool_results.append({
                                "tool_call_id": tool_call["id"],
                                "function_name": function_name,
                                "error": f"Unknown function: {function_name}"
                            })
                    
                    all_tool_results.extend(tool_results)
                    
                    # Build messages for follow-up
                    current_messages.append(current_message)
                    
                    for tr in tool_results:
                        current_messages.append({
                            "role": "tool",
                            "tool_call_id": tr["tool_call_id"],
                            "content": json.dumps(tr.get("result", {"error": tr.get("error")}), ensure_ascii=False)
                        })
                    
                    # Make follow-up request
                    follow_up_payload = {
                        "model": self.config.model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            *current_messages
                        ],
                        "tools": TOOLS,
                        "tool_choice": "auto"
                    }
                    
                    follow_up_response = await client.post(
                        f"{self.config.api_base}/chat/completions",
                        headers=headers,
                        json=follow_up_payload
                    )
                    
                    if follow_up_response.status_code != 200:
                        return {"error": f"Follow-up API error: {follow_up_response.status_code}", "content": None}
                    
                    follow_up_data = follow_up_response.json()
                    current_message = follow_up_data["choices"][0]["message"]
                
                return {
                    "content": current_message.get("content", ""),
                    "tool_results": all_tool_results
                }
                
        except httpx.TimeoutException:
            return {"error": "Request timeout", "content": None}
        except Exception as e:
            return {"error": str(e), "content": None}
    
    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        tool_handlers: Dict[str, Callable]
    ):
        """
        Stream chat response from OpenAI API
        Yields chunks of content or tool results
        """
        if not self.is_configured():
            yield {"type": "error", "content": "API key not configured"}
            return
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                *messages
            ],
            "tools": TOOLS,
            "tool_choice": "auto",
            "stream": True
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.config.api_base}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        yield {"type": "error", "content": f"API error: {response.status_code}"}
                        return
                    
                    accumulated_message = {}
                    tool_calls_buffer = {}
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break
                            
                            try:
                                chunk = json.loads(data_str)
                                delta = chunk["choices"][0].get("delta", {})
                                
                                # Handle content
                                if "content" in delta and delta["content"]:
                                    yield {"type": "content", "content": delta["content"]}
                                
                                # Handle tool calls
                                if "tool_calls" in delta:
                                    for tc in delta["tool_calls"]:
                                        idx = tc.get("index", 0)
                                        if idx not in tool_calls_buffer:
                                            tool_calls_buffer[idx] = {
                                                "id": "",
                                                "function": {"name": "", "arguments": ""}
                                            }
                                        
                                        if "id" in tc:
                                            tool_calls_buffer[idx]["id"] = tc["id"]
                                        if "function" in tc:
                                            if "name" in tc["function"]:
                                                tool_calls_buffer[idx]["function"]["name"] = tc["function"]["name"]
                                            if "arguments" in tc["function"]:
                                                tool_calls_buffer[idx]["function"]["arguments"] += tc["function"]["arguments"]
                                
                            except json.JSONDecodeError:
                                continue
                    
                    # Process tool calls if any
                    if tool_calls_buffer:
                        yield {"type": "tool_start", "count": len(tool_calls_buffer)}
                        
                        tool_results = []
                        for idx in sorted(tool_calls_buffer.keys()):
                            tc = tool_calls_buffer[idx]
                            function_name = tc["function"]["name"]
                            # Handle potential JSON parsing issues
                            try:
                                function_args = json.loads(tc["function"]["arguments"])
                            except json.JSONDecodeError as e:
                                print(f"[DEBUG] Stream JSON decode error for {function_name}: {e}")
                                print(f"[DEBUG] Raw arguments: {tc['function']['arguments']}")
                                function_args = {}
                            
                            yield {"type": "tool_call", "name": function_name, "args": function_args}
                            
                            if function_name in tool_handlers:
                                try:
                                    result = await tool_handlers[function_name](**function_args)
                                    tool_results.append({
                                        "tool_call_id": tc["id"],
                                        "result": result
                                    })
                                    yield {"type": "tool_result", "name": function_name, "result": result}
                                except Exception as e:
                                    tool_results.append({
                                        "tool_call_id": tc["id"],
                                        "error": str(e)
                                    })
                                    yield {"type": "tool_error", "name": function_name, "error": str(e)}
                        
                        # Make follow-up request for final response
                        follow_up_messages = list(messages)
                        follow_up_messages.append({
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "id": tc["id"],
                                    "type": "function",
                                    "function": {
                                        "name": tc["function"]["name"],
                                        "arguments": tc["function"]["arguments"]
                                    }
                                }
                                for tc in tool_calls_buffer.values()
                            ]
                        })
                        
                        for tr in tool_results:
                            follow_up_messages.append({
                                "role": "tool",
                                "tool_call_id": tr["tool_call_id"],
                                "content": json.dumps(tr.get("result", {"error": tr.get("error")}), ensure_ascii=False)
                            })
                        
                        # Follow-up without streaming for simplicity
                        follow_up_payload = {
                            "model": self.config.model,
                            "messages": [
                                {"role": "system", "content": SYSTEM_PROMPT},
                                *follow_up_messages
                            ]
                        }
                        
                        async with client.stream(
                            "POST",
                            f"{self.config.api_base}/chat/completions",
                            headers=headers,
                            json=follow_up_payload
                        ) as follow_up_response:
                            if follow_up_response.status_code == 200:
                                async for line in follow_up_response.aiter_lines():
                                    if line.startswith("data: "):
                                        data_str = line[6:]
                                        if data_str == "[DONE]":
                                            break
                                        try:
                                            chunk = json.loads(data_str)
                                            delta = chunk["choices"][0].get("delta", {})
                                            if "content" in delta and delta["content"]:
                                                yield {"type": "content", "content": delta["content"]}
                                        except json.JSONDecodeError:
                                            continue
                                        
        except httpx.TimeoutException:
            yield {"type": "error", "content": "Request timeout"}
        except Exception as e:
            yield {"type": "error", "content": str(e)}


# Global service instance
ai_service = AIService()
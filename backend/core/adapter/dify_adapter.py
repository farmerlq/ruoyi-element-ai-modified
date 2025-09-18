import httpx
import json
from typing import Dict, Any, AsyncGenerator, Optional
from ..parser import DifyParser
from .base import BaseAdapter, ChatRequest, ChatResponse

class DifyAdapter(BaseAdapter):
    """Dify平台适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost/v1")
        # 使用智能体配置中的api_key
        self.api_key = config.get("api_key", "")
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        self.parser = DifyParser()
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """处理普通聊天请求"""
        # 根据智能体配置中的type类型判断是调用工作流接口还是聊天接口
        agent_type = self.config.get("type", "chat")  # 默认是chat类型
        is_workflow = agent_type == "workflow"
        
        # 确定端点
        endpoint = "/workflows/run" if is_workflow else "/chat-messages"
        
        if is_workflow:
            # 工作流需要不同的参数结构
            # 获取基础inputs配置
            inputs = self.config.get("workflow_inputs", {}).copy()
            
            # 将查询内容添加到inputs中
            if request.query:
                inputs["query"] = request.query
            
            payload = {
                "inputs": inputs,
                "response_mode": "blocking",
                "user": str(request.user_id)
            }
        else:
            # 聊天接口参数
            payload = {
                "inputs": {},
                "query": request.query,
                "user": str(request.user_id),
                "response_mode": "blocking"
            }
        
        if request.conversation_id:
            payload["conversation_id"] = request.conversation_id
            
        response = await self.client.post(endpoint, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # 根据端点类型使用不同的解析方法
        if is_workflow:
            # 如果是workflow，使用workflow解析方法
            workflow_data = data.get("data", {})
            outputs = workflow_data.get("outputs", {})
            
            # 提取文本内容
            message = ""
            if isinstance(outputs, dict):
                message = outputs.get("text", "")
                if not message:
                    for key, value in outputs.items():
                        if isinstance(value, str):
                            message = value
                            break
            
            return ChatResponse(
                message=message,
                conversation_id=workflow_data.get("id"),
                message_id=data.get("task_id"),
                metadata={
                    "workflow_run_id": data.get("workflow_run_id"),
                    "task_id": data.get("task_id"),
                    "status": workflow_data.get("status"),
                    "elapsed_time": workflow_data.get("elapsed_time"),
                    "total_tokens": workflow_data.get("total_tokens"),
                    "total_steps": workflow_data.get("total_steps"),
                    "created_at": workflow_data.get("created_at"),
                    "finished_at": workflow_data.get("finished_at"),
                    "error": workflow_data.get("error")
                }
            )
        else:
            # 如果是chat-messages，使用chat解析方法
            return self.parser.parse_blocking_response(data)
    
    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[ChatResponse, None]:
        """处理流式聊天请求
        
        支持解析的事件类型:
        1. message: LLM 返回文本块事件
        2. message_end: 消息结束事件
        3. tts_message: TTS 音频流事件
        4. tts_message_end: TTS 音频流结束事件
        5. message_replace: 消息内容替换事件
        6. error: 错误事件
        7. ping: 心跳事件
        8. text_chunk: Workflow文本块事件
        9. workflow_finished: Workflow完成事件
        10. node_started: 节点开始执行事件
        11. node_finished: 节点执行结束事件
        12. workflow_started: Workflow开始执行事件
        """
        # 根据智能体配置中的type类型判断是调用工作流接口还是聊天接口
        agent_type = self.config.get("type", "chat")  # 默认是chat类型
        is_workflow = agent_type == "workflow"
        
        # 确定端点
        endpoint = "/workflows/run" if is_workflow else "/chat-messages"
        
        if is_workflow:
            # 工作流需要不同的参数结构
            # 获取基础inputs配置
            inputs = self.config.get("workflow_inputs", {}).copy()
            
            # 将查询内容添加到inputs中
            if request.query:
                inputs["query"] = request.query
            
            payload = {
                "inputs": inputs,
                "response_mode": "streaming",
                "user": str(request.user_id)
            }
        else:
            # 聊天接口参数
            payload = {
                "inputs": {},
                "query": request.query,
                "user": str(request.user_id),
                "response_mode": "streaming"
            }
        
        if request.conversation_id:
            payload["conversation_id"] = request.conversation_id
            
        async with self.client.stream("POST", endpoint, json=payload) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]  # 移除 "data: " 前缀
                    if data_str.strip() == "[DONE]":
                        break
                    
                    try:
                        data = json.loads(data_str)
                        event = data.get("event")
                        
                        # 根据是否使用workflow进行不同处理
                        if is_workflow:
                            # 处理workflow流式事件
                            # 8. 处理 text_chunk 事件 - Workflow文本块事件
                            if event == "text_chunk":
                                chunk_data = data.get("data", {})
                                text = chunk_data.get("text", "")
                                
                                yield ChatResponse(
                                    message=text,
                                    conversation_id=data.get("workflow_run_id"),
                                    message_id=data.get("task_id"),
                                    metadata={
                                        "event": event,
                                        "workflow_run_id": data.get("workflow_run_id"),
                                        "task_id": data.get("task_id"),
                                        "from_variable_selector": chunk_data.get("from_variable_selector")
                                    }
                                )
                            # 9. 处理 workflow_finished 事件 - Workflow完成事件
                            elif event == "workflow_finished":
                                # 工作流完成，发送最终响应
                                workflow_data = data.get("data", {})
                                outputs = workflow_data.get("outputs", {})
                                message = ""
                                if isinstance(outputs, dict):
                                    message = outputs.get("text", "")
                                    # 如果没有text字段，尝试其他可能的文本字段
                                    if not message:
                                        for key, value in outputs.items():
                                            if isinstance(value, str):
                                                message = value
                                                break
                                
                                yield ChatResponse(
                                    message=message,
                                    conversation_id=data.get("workflow_run_id"),
                                    message_id=data.get("task_id"),
                                    metadata={
                                        "event": event,
                                        "status": workflow_data.get("status"),
                                        "elapsed_time": workflow_data.get("elapsed_time"),
                                        "total_tokens": workflow_data.get("total_tokens"),
                                        "total_steps": workflow_data.get("total_steps"),
                                        "finished_at": workflow_data.get("finished_at"),
                                        "error": workflow_data.get("error")
                                    }
                                )
                            # 12. 处理 workflow_started 事件 - Workflow开始执行事件
                            elif event == "workflow_started":
                                yield ChatResponse(
                                    message="",
                                    conversation_id=data.get("workflow_run_id"),
                                    message_id=data.get("task_id"),
                                    metadata={
                                        "event": event,
                                        "workflow_run_id": data.get("workflow_run_id"),
                                        "task_id": data.get("task_id"),
                                        "workflow_data": data.get("data")
                                    }
                                )
                            # 10. 处理 node_started 事件 - 节点开始执行事件
                            elif event == "node_started":
                                yield ChatResponse(
                                    message="",
                                    conversation_id=data.get("workflow_run_id"),
                                    message_id=data.get("task_id"),
                                    metadata={
                                        "event": event,
                                        "workflow_run_id": data.get("workflow_run_id"),
                                        "task_id": data.get("task_id"),
                                        "node_data": data.get("data")
                                    }
                                )
                            # 11. 处理 node_finished 事件 - 节点执行结束事件
                            elif event == "node_finished":
                                yield ChatResponse(
                                    message="",
                                    conversation_id=data.get("workflow_run_id"),
                                    message_id=data.get("task_id"),
                                    metadata={
                                        "event": event,
                                        "workflow_run_id": data.get("workflow_run_id"),
                                        "task_id": data.get("task_id"),
                                        "node_data": data.get("data")
                                    }
                                )
                        else:
                            # 处理chat-messages流式事件
                            # 1. 处理 message 事件 - LLM 返回文本块事件
                            if event == "message":
                                # LLM 返回文本块事件
                                yield ChatResponse(
                                    message=data.get("answer", ""),
                                    conversation_id=None,
                                    message_id=data.get("message_id"),
                                    metadata={
                                        "event": event,
                                        "task_id": data.get("task_id"),
                                        "id": data.get("id"),
                                        "created_at": data.get("created_at")
                                    }
                                )
                            
                            # 2. 处理 message_end 事件 - 消息结束事件
                            elif event == "message_end":
                                # 消息结束事件
                                yield ChatResponse(
                                    message="",
                                    conversation_id=None,
                                    message_id=data.get("message_id"),
                                    metadata={
                                        "event": event,
                                        "task_id": data.get("task_id"),
                                        "metadata": data.get("metadata"),
                                        "usage": data.get("usage"),
                                        "retriever_resources": data.get("retriever_resources")
                                    }
                                )
                            
                            # 3. 处理 tts_message 事件 - TTS 音频流事件
                            elif event == "tts_message":
                                # TTS 音频流事件
                                yield ChatResponse(
                                    message="",
                                    conversation_id=None,
                                    message_id=data.get("message_id"),
                                    metadata={
                                        "event": event,
                                        "task_id": data.get("task_id"),
                                        "audio": data.get("audio"),
                                        "created_at": data.get("created_at")
                                    }
                                )
                            
                            # 4. 处理 tts_message_end 事件 - TTS 音频流结束事件
                            elif event == "tts_message_end":
                                # TTS 音频流结束事件
                                yield ChatResponse(
                                    message="",
                                    conversation_id=None,
                                    message_id=data.get("message_id"),
                                    metadata={
                                        "event": event,
                                        "task_id": data.get("task_id"),
                                        "audio": data.get("audio"),
                                        "created_at": data.get("created_at")
                                    }
                                )
                            
                            # 5. 处理 message_replace 事件 - 消息内容替换事件
                            elif event == "message_replace":
                                # 消息内容替换事件
                                yield ChatResponse(
                                    message=data.get("answer", ""),
                                    conversation_id=None,
                                    message_id=data.get("message_id"),
                                    metadata={
                                        "event": event,
                                        "task_id": data.get("task_id"),
                                        "created_at": data.get("created_at")
                                    }
                                )
                            
                            # 6. 处理 error 事件 - 错误事件
                            elif event == "error":
                                # 错误事件
                                yield ChatResponse(
                                    message="",
                                    conversation_id=None,
                                    message_id=data.get("message_id"),
                                    metadata={
                                        "event": event,
                                        "task_id": data.get("task_id"),
                                        "status": data.get("status"),
                                        "code": data.get("code"),
                                        "error_message": data.get("message")
                                    }
                                )
                            
                            # 7. 处理 ping 事件 - 心跳事件
                            elif event == "ping":
                                # 心跳事件，不需要返回内容
                                pass
                    
                    except json.JSONDecodeError:
                        continue
    
    async def get_conversation_history(self, conversation_id: str) -> Dict[str, Any]:
        """获取对话历史"""
        response = await self.client.get(f"/messages?conversation_id={conversation_id}")
        response.raise_for_status()
        return response.json()
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """删除对话"""
        try:
            response = await self.client.delete(f"/conversations/{conversation_id}")
            response.raise_for_status()
            return True
        except:
            return False
    
    async def close(self):
        """关闭客户端连接"""
        await self.client.aclose()
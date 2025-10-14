import json
from typing import Dict, Any, AsyncGenerator, Optional, Union
from ..adapter.base import ChatResponse

class DifyParser:
    """Dify响应解析器
    
    支持以下响应格式：
    
    1. ChatCompletionResponse (blocking mode):
       - message_id: 消息唯一 ID
       - mode: App 模式，固定为 chat
       - answer: 完整回复内容
       - metadata: 元数据
       - usage: 模型用量信息
       - retriever_resources: 引用和归属分段列表
       - created_at: 消息创建时间戳
    
    2. ChunkChatCompletionResponse (streaming mode):
       流式块中根据 event 不同，结构也不同：
       
       普通聊天事件:
       - event: message - LLM 返回文本块事件
       - event: message_end - 消息结束事件
       - event: tts_message - TTS 音频流事件
       - event: tts_message_end - TTS 音频流结束事件
       - event: message_replace - 消息内容替换事件
       - event: error - 错误事件
       - event: ping - 心跳事件
       
       工作流事件:
       - event: text_chunk - 工作流文本块事件
       - event: workflow_started - Workflow开始执行事件
       - event: workflow_finished - Workflow完成事件
       - event: node_started - 节点开始执行事件
       - event: node_finished - 节点执行结束事件
    """
    
    @staticmethod
    def parse_blocking_response(data: Dict[str, Any], is_workflow: bool = False) -> ChatResponse:
        """
        解析阻塞模式下的响应数据 (ChatCompletionResponse)
        
        Args:
            data (Dict[str, Any]): Dify API返回的blocking模式响应数据
            is_workflow (bool): 是否为工作流模式
            
        Returns:
            ChatResponse: 解析后的统一响应格式
            
        Response format:
        普通聊天模式:
        {
            "message_id": "message_id",
            "mode": "chat",
            "answer": "完整回复内容",
            "metadata": {},
            "usage": {},
            "retriever_resources": [],
            "created_at": 1705395332
        }
        
        工作流模式:
        {
            "data": {
                "id": "workflow_run_id",
                "workflow_id": "workflow_id",
                "status": "succeeded",
                "outputs": {
                    "output": "回复内容"
                },
                "error": "",
                "elapsed_time": 5.123,
                "total_tokens": 100,
                "total_steps": 3,
                "created_at": 1705395332,
                "finished_at": 1705395337
            },
            "task_id": "task_id",
            "workflow_run_id": "workflow_run_id"
        }
        """
        if is_workflow:
            # 工作流模式响应处理
            workflow_data = data.get("data", {})
            outputs = workflow_data.get("outputs", {})
            
            # 提取完整的响应结构
            
            # 提取回复内容
            message = ""
            if isinstance(outputs, dict):
                # 尝试从outputs中提取文本内容
                message = outputs.get("output", "")
                # 如果没有output字段，尝试其他可能的文本字段
                if not message:
                    for key, value in outputs.items():
                        if isinstance(value, str) and value.strip():
                            message = value
                            break
            
            # 提取消息内容和长度
            
            return ChatResponse(
                message=message,
                conversation_id=data.get("workflow_run_id"),
                message_id=data.get("task_id"),
                metadata={
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
            # 普通聊天模式响应处理
            return ChatResponse(
                message=data.get("answer", ""),
                conversation_id=data.get("conversation_id"),  # 使用API返回的conversation_id
                message_id=data.get("message_id"),
                metadata={
                    "mode": data.get("mode"),
                    "metadata": data.get("metadata"),
                    "usage": data.get("usage"),
                    "retriever_resources": data.get("retriever_resources"),
                    "created_at": data.get("created_at")
                }
            )
    
    @staticmethod
    def _create_text_chunk_response(data: Dict[str, Any], event: str, message: str, conversation_id_key: str = "conversation_id", metadata: Optional[Dict[str, Any]] = None) -> ChatResponse:
        """创建文本块响应的辅助方法
        
        Args:
            data (Dict[str, Any]): 原始数据
            event (str): 事件类型
            message (str): 消息内容
            conversation_id_key (str): conversation_id的键名
            metadata (Dict[str, Any]): 额外的元数据
        
        Returns:
            ChatResponse: 构造的响应对象
        """
        base_metadata = {
            "event": event,
            "task_id": data.get("task_id")
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        return ChatResponse(
            message=message,
            conversation_id=data.get(conversation_id_key),
            message_id=data.get("message_id") if event == "message" else data.get("task_id"),
            metadata=base_metadata
        )
    
    @staticmethod
    async def parse_streaming_response(response_text: str) -> AsyncGenerator[ChatResponse, None]:
        """解析流式响应数据 (ChunkChatCompletionResponse)
        
        Args:
            response_text (str): Dify API返回的流式响应文本
            
        Yields:
            ChatResponse: 解析后的统一响应格式
            
        流式数据格式:
        data: {"event": "...", ...}
        
        支持解析的事件类型:
        普通聊天事件:
        1. message: LLM 返回文本块事件
        2. message_end: 消息结束事件
        3. tts_message: TTS 音频流事件
        4. tts_message_end: TTS 音频流结束事件
        5. message_replace: 消息内容替换事件
        6. error: 错误事件
        7. ping: 心跳事件
        
        工作流事件:
        8. text_chunk: 工作流文本块事件
        9. workflow_started: Workflow开始执行事件
        10. workflow_finished: Workflow完成事件
        11. node_started: 节点开始执行事件
        12. node_finished: 节点执行结束事件
        """
        lines = response_text.split('\n\n')
        
        for line in lines:
            if line.startswith("data: "):
                data_str = line[6:]  # 移除 "data: " 前缀
                if data_str.strip() == "[DONE]":
                    break
                
                try:
                    data = json.loads(data_str)
                    event = data.get("event")
                    
                    # 1. 处理 message 事件 - LLM 返回文本块事件
                    if event == "message":
                        # 从message事件中提取文本内容
                        message_content = data.get("answer", "")
                        workflow_run_id = data.get("conversation_id")
                        
                        # 保持message事件不变，不转换为text_chunk
                        response = DifyParser._create_text_chunk_response(
                            data,
                            "message",  # 保持原始事件类型
                            message_content,
                            "conversation_id",
                            {
                                "workflow_run_id": workflow_run_id,
                                "text": message_content,
                                "original_event": "message",
                                "id": data.get("id"),
                                "created_at": data.get("created_at")
                            }
                        )
                        
                        yield response
                    
                    # 2. 处理 agent_message 事件 - Agent模式下返回文本块事件
                    elif event == "agent_message":
                        # 从agent_message事件中提取文本内容
                        message_content = data.get("answer", "")
                        workflow_run_id = data.get("conversation_id")
                        
                        response = DifyParser._create_text_chunk_response(
                            data,
                            "agent_message",  # 保持原始事件类型
                            message_content,
                            "conversation_id",
                            {
                                "workflow_run_id": workflow_run_id,
                                "text": message_content,
                                "original_event": "agent_message",
                                "id": data.get("id"),
                                "created_at": data.get("created_at")
                            }
                        )
                        
                        yield response
                    
                    # 3. 处理 agent_thought 事件 - Agent模式下有关Agent思考步骤的相关内容
                    elif event == "agent_thought":
                        # 构造符合agent_thought格式的数据结构
                        yield ChatResponse(
                            message="",  # 思考事件消息内容为空，不将思考内容放入message字段
                            conversation_id=data.get("conversation_id"),
                            message_id=data.get("message_id"),
                            metadata={
                                "event": event,
                                "id": data.get("id"),
                                "task_id": data.get("task_id"),
                                "position": data.get("position"),
                                "thought": data.get("thought"),
                                "observation": data.get("observation"),
                                "tool": data.get("tool"),
                                "tool_input": data.get("tool_input"),
                                "created_at": data.get("created_at"),
                                "message_files": data.get("message_files", []),
                                "file_id": data.get("file_id"),
                                "conversation_id": data.get("conversation_id")
                            }
                        )
                    
                    # 4. 处理 message_file 事件 - 文件事件，表示有新文件需要展示
                    elif event == "message_file":
                        yield ChatResponse(
                            message="",
                            conversation_id=data.get("conversation_id"),
                            message_id=data.get("id"),
                            metadata={
                                "event": event,
                                "id": data.get("id"),
                                "type": data.get("type"),
                                "belongs_to": data.get("belongs_to"),
                                "url": data.get("url"),
                                "conversation_id": data.get("conversation_id")
                            }
                        )
                    
                    # 5. 处理 message_end 事件 - 消息结束事件
                    elif event == "message_end":
                        # 消息结束事件
                        yield ChatResponse(
                            message="",  # 结束事件消息内容为空
                            conversation_id=data.get("conversation_id"),
                            message_id=data.get("message_id"),
                            metadata={
                                "event": event,
                                "task_id": data.get("task_id"),
                                "message_id": data.get("message_id"),
                                "conversation_id": data.get("conversation_id"),
                                "metadata": data.get("metadata"),
                                "usage": data.get("usage"),
                                "retriever_resources": data.get("retriever_resources")
                            }
                        )
                    
                    # 6. 处理 tts_message 事件 - TTS 音频流事件
                    elif event == "tts_message":
                        # TTS 音频流事件，即语音合成输出
                        # 内容是Mp3格式的音频块，使用 base64 编码后的字符串
                        yield ChatResponse(
                            message="",
                            conversation_id=data.get("conversation_id"),
                            message_id=data.get("message_id"),
                            metadata={
                                "event": event,
                                "task_id": data.get("task_id"),
                                "message_id": data.get("message_id"),
                                "audio": data.get("audio"),
                                "created_at": data.get("created_at")
                            }
                        )
                    
                    # 7. 处理 tts_message_end 事件 - TTS 音频流结束事件
                    elif event == "tts_message_end":
                        # TTS 音频流结束事件，收到这个事件表示音频流返回结束
                        yield ChatResponse(
                            message="",
                            conversation_id=data.get("conversation_id"),
                            message_id=data.get("message_id"),
                            metadata={
                                "event": event,
                                "task_id": data.get("task_id"),
                                "message_id": data.get("message_id"),
                                "audio": data.get("audio"),  # 结束事件是没有音频的，所以这里是空字符串
                                "created_at": data.get("created_at")
                            }
                        )
                    
                    # 8. 处理 message_replace 事件 - 消息内容替换事件
                    elif event == "message_replace":
                        # 消息内容替换事件
                        # 开启内容审查和审查输出内容时，若命中了审查条件，则会通过此事件替换消息内容为预设回复
                        yield ChatResponse(
                            message=data.get("answer", ""),
                            conversation_id=data.get("conversation_id"),
                            message_id=data.get("message_id"),
                            metadata={
                                "event": event,
                                "task_id": data.get("task_id"),
                                "message_id": data.get("message_id"),
                                "created_at": data.get("created_at")
                            }
                        )
                    
                    # 9. 处理 error 事件 - 错误事件
                    elif event == "error":
                        # 流式输出过程中出现的异常会以 stream event 形式输出
                        # 收到异常事件后即结束
                        yield ChatResponse(
                            message="",
                            conversation_id=data.get("conversation_id"),
                            message_id=data.get("message_id"),
                            metadata={
                                "event": event,
                                "task_id": data.get("task_id"),
                                "message_id": data.get("message_id"),
                                "status": data.get("status"),
                                "code": data.get("code"),
                                "error_message": data.get("message")
                            }
                        )
                    
                    # 10. 处理 ping 事件 - 心跳事件
                    elif event == "ping":
                        # 每 10s 一次的 ping 事件，保持连接存活
                        yield ChatResponse(
                            message="",
                            conversation_id=None,
                            message_id=None,
                            metadata={
                                "event": event
                            }
                        )
                    
                    # 11. 处理 text_chunk 事件 - 工作流文本块事件
                    elif event == "text_chunk":
                        chunk_data = data.get("data", {})
                        text = chunk_data.get("text", "")
                        
                        response = DifyParser._create_text_chunk_response(
                            data, 
                            event, 
                            text,
                            "workflow_run_id",
                            {
                                "workflow_run_id": data.get("workflow_run_id"),
                                "text": text,
                                "from_variable_selector": chunk_data.get("from_variable_selector", [])
                            }
                        )
                        
                        # 处理text_chunk事件
                        yield response
                    
                    # 12. 处理 workflow_finished 事件 - Workflow完成事件
                    elif event == "workflow_finished":
                        # 工作流完成事件
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
                    
                    # 13. 处理 workflow_started 事件 - Workflow开始执行事件
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
                    
                    # 14. 处理 node_started 事件 - 节点开始执行事件
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
                    
                    # 15. 处理 node_finished 事件 - 节点执行结束事件
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
                        
                except json.JSONDecodeError:
                    # 忽略无法解析的行
                    continue
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
    def parse_blocking_response(data: Dict[str, Any]) -> ChatResponse:
        """
        解析阻塞模式下的响应数据 (ChatCompletionResponse)
        
        Args:
            data (Dict[str, Any]): Dify API返回的blocking模式响应数据
            
        Returns:
            ChatResponse: 解析后的统一响应格式
            
        Response format:
        {
            "message_id": "message_id",
            "mode": "chat",
            "answer": "完整回复内容",
            "metadata": {},
            "usage": {},
            "retriever_resources": [],
            "created_at": 1705395332
        }
        """
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
                        # LLM 返回文本块事件
                        yield ChatResponse(
                            message=data.get("answer", ""),
                            conversation_id=data.get("conversation_id"),
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
                        # 消息结束事件，表示文本流式返回结束
                        yield ChatResponse(
                            message="",
                            conversation_id=data.get("conversation_id"),
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
                        # TTS 音频流事件，即语音合成输出
                        # 内容是Mp3格式的音频块，使用 base64 编码后的字符串
                        yield ChatResponse(
                            message="",
                            conversation_id=data.get("conversation_id"),
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
                        # TTS 音频流结束事件，收到这个事件表示音频流返回结束
                        yield ChatResponse(
                            message="",
                            conversation_id=data.get("conversation_id"),
                            message_id=data.get("message_id"),
                            metadata={
                                "event": event,
                                "task_id": data.get("task_id"),
                                "audio": data.get("audio"),  # 结束事件是没有音频的，所以这里是空字符串
                                "created_at": data.get("created_at")
                            }
                        )
                    
                    # 5. 处理 message_replace 事件 - 消息内容替换事件
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
                                "created_at": data.get("created_at")
                            }
                        )
                    
                    # 6. 处理 error 事件 - 错误事件
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
                                "status": data.get("status"),
                                "code": data.get("code"),
                                "error_message": data.get("message")
                            }
                        )
                    
                    # 7. 处理 ping 事件 - 心跳事件
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
                    
                    # 8. 处理 text_chunk 事件 - 工作流文本块事件
                    elif event == "text_chunk":
                        chunk_data = data.get("data", {})
                        text = chunk_data.get("text", "")
                        
                        yield ChatResponse(
                            message=text,
                            conversation_id=data.get("workflow_run_id"),
                            message_id=data.get("task_id"),
                            metadata={
                                "event": event,
                                "task_id": data.get("task_id"),
                                "workflow_run_id": data.get("workflow_run_id"),
                                "text": text,
                                "from_variable_selector": chunk_data.get("from_variable_selector", [])
                            }
                        )
                    
                    # 9. 处理 workflow_finished 事件 - Workflow完成事件
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
                    
                    # 10. 处理 workflow_started 事件 - Workflow开始执行事件
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
                    
                    # 11. 处理 node_started 事件 - 节点开始执行事件
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
                    
                    # 12. 处理 node_finished 事件 - 节点执行结束事件
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
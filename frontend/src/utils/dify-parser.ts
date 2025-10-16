/**
 * Dify 流式响应解析器
 * 用于处理 Dify 平台的 SSE 流式响应
 */
export class DifyRenderer {
  private finished: boolean = false;
  private onDataCallback: ((content: string, metadata?: any) => void) | null = null;
  private onWorkflowEventCallback: ((eventData: any) => void) | null = null;
  private onCompleteCallback: (() => void) | null = null;
  private onErrorCallback: ((error: Error) => void) | null = null;

  constructor() {
    this.reset();
  }

  /**
   * 重置解析器状态
   */
  public reset(): void {
    this.finished = false;
  }

  /**
   * 处理数据块
   * @param chunk 数据块
   * @param onData 数据回调
   * @param onWorkflowEvent 工作流事件回调
   * @param onComplete 完成回调
   * @param onError 错误回调
   */
  public handleChunk(
    chunk: any,
    onData?: (content: string, metadata?: any) => void,
    onWorkflowEvent?: (eventData: any) => void,
    onComplete?: () => void,
    onError?: (error: Error) => void,
  ): void {
    // 设置回调函数
    if (onData)
      this.onDataCallback = onData;
    if (onWorkflowEvent)
      this.onWorkflowEventCallback = onWorkflowEvent;
    if (onComplete)
      this.onCompleteCallback = onComplete;
    if (onError)
      this.onErrorCallback = onError;

    try {
      // 处理流式响应数据
      if (typeof chunk === 'string') {
        // 特殊情况：检查是否包含[DONE]标记（这是后端API的正常结束标记）
        if (chunk.includes('[DONE]')) {
          // 提取[DONE]之前的所有内容
          const contentBeforeDone = chunk.split('[DONE]')[0].trim();
          if (contentBeforeDone) {
            this.handleChunk(contentBeforeDone, onData, onWorkflowEvent, onComplete, onError);
          }
          // 通知流结束
          this.notifyEnd();
          return;
        }

        // 按SSE格式分割数据（使用两个换行符作为分隔符）
        const events = chunk.split('\n\n');
        for (const event of events) {
          const trimmedEvent = event.trim();
          if (!trimmedEvent)
            continue;

          // 处理 SSE 格式数据
          if (trimmedEvent.startsWith('data:')) {
            const dataStr = trimmedEvent.substring(5).trim(); // 去掉 "data:" 前缀
            if (dataStr) {
              try {
                // 特殊情况：处理包含data: {"event": ...}格式
                if (dataStr.startsWith('{') && dataStr.endsWith('}')) {
                  // 检查是否是单个JSON对象
                  if (dataStr.indexOf('{') === dataStr.lastIndexOf('{')
                    && dataStr.indexOf('}') === dataStr.lastIndexOf('}')) {
                    // 单个JSON对象
                    const data = JSON.parse(dataStr);
                    this.processEventData(data);
                  }
                  else {
                    // 多个JSON对象在一行的情况
                    this.processMultiJson(dataStr);
                  }
                }
                // 处理普通文本
                else {
                  if (this.onDataCallback && dataStr.trim() && dataStr !== '[等待内容...]') {
                    this.onDataCallback(dataStr);
                  }
                }
              }
              catch (jsonError) {
                // 如果不是JSON，检查是否包含关键信息
                if (trimmedEvent.toLowerCase().includes('error')) {
                  if (this.onErrorCallback) {
                    this.onErrorCallback(new Error(`响应包含错误信息: ${trimmedEvent}`));
                  }
                }
                else if (trimmedEvent.toLowerCase().includes('content')
                  || trimmedEvent.toLowerCase().includes('answer')
                  || trimmedEvent.toLowerCase().includes('text')) {
                  // 尝试提取可能的内容
                  const contentMatch = trimmedEvent.match(/"(content|answer|text)":"([^"]*)"/i);
                  if (contentMatch && contentMatch[2]) {
                    if (this.onDataCallback && contentMatch[2].trim() && contentMatch[2] !== '[等待内容...]') {
                      this.onDataCallback(contentMatch[2]);
                    }
                  }
                  else {
                    // 当作普通文本处理
                    if (this.onDataCallback && dataStr.trim() && dataStr !== '[等待内容...]') {
                      this.onDataCallback(dataStr);
                    }
                  }
                }
                else {
                  // 当作普通文本处理
                  if (this.onDataCallback && dataStr.trim() && dataStr !== '[等待内容...]') {
                    this.onDataCallback(dataStr);
                  }
                }
              }
            }
          }
          // 处理非SSE格式但可能包含内容的情况
          else if (trimmedEvent.startsWith('{') && trimmedEvent.endsWith('}')) {
            try {
              const data = JSON.parse(trimmedEvent);
              this.processEventData(data);
            }
            catch {
              if (this.onDataCallback) {
                this.onDataCallback(trimmedEvent);
              }
            }
          }
          // 处理纯文本内容
          else if (trimmedEvent.length > 0) {
            // 跳过只包含控制字符的行
            if (this.hasVisibleCharacters(trimmedEvent)) {
              if (this.onDataCallback) {
                this.onDataCallback(trimmedEvent);
              }
            }
          }
        }
      }
    }
    catch (error) {
      if (this.onErrorCallback && error instanceof Error) {
        this.onErrorCallback(error);
      }
    }
  }

  /**
   * 处理多个JSON对象在一行的情况
   */
  private processMultiJson(dataStr: string): void {
    try {
      // 简单的处理方式：查找所有的JSON对象
      const jsonObjects = this.extractJsonObjects(dataStr);
      for (const jsonObj of jsonObjects) {
        this.processEventData(jsonObj);
      }
    }
    catch (error) {
      // 处理多JSON对象时出错
    }
  }

  /**
   * 从字符串中提取JSON对象
   */
  private extractJsonObjects(str: string): any[] {
    const objects: any[] = [];
    let depth = 0;
    let start = -1;

    for (let i = 0; i < str.length; i++) {
      if (str[i] === '{') {
        if (depth === 0) {
          start = i;
        }
        depth++;
      }
      else if (str[i] === '}') {
        depth--;
        if (depth === 0 && start !== -1) {
          try {
            const jsonStr = str.substring(start, i + 1);
            const obj = JSON.parse(jsonStr);
            objects.push(obj);
          }
          catch {
            // 如果解析失败，忽略这个对象
          }
          start = -1;
        }
      }
    }

    return objects;
  }

  /**
   * 修复大括号样式问题
   */
  private processEventData(data: any): void {
    if (!data || typeof data !== 'object')
      return;

    const event = data.event;

    switch (event) {
      case 'message':
      case 'agent_message':
      case 'text_chunk': {
        let content = '';

        if (data.content) {
          content = data.content;
        }
        else if (data.answer) {
          content = data.answer;
        }
        else if (data.text) {
          content = data.text;
        }
        else if (data.data && data.data.text) {
          content = data.data.text;
        }
        else if (data.data && data.data.content) {
          content = data.data.content;
        }
        else if (data.message) {
          content = data.message;
        }
        else {
          content = this.findContentInObject(data);
        }

        // 修复'text_chunk'问题：确保内容不为空且不包含事件类型名称
        if (content.trim() && content !== '[等待内容...]' && content !== 'text_chunk') {
          if (this.onDataCallback) {
            this.onDataCallback(content, data);
          }
        }
        else {
          // 不再传递空字符串或'text_chunk'，避免在UI中出现额外内容
        }
        break;
      }

      case 'workflow_finished': {
        const eventData = {
          status: data.status,
          elapsed_time: data.elapsed_time,
          total_tokens: data.total_tokens,
          total_steps: data.total_steps,
          finished_at: data.finished_at,
          error: data.error,
          outputs: data.outputs,
          ...(data.data || {}), // 也包含可能的data字段
        };
        if (this.onWorkflowEventCallback) {
          this.onWorkflowEventCallback({
            event: 'workflow_finished',
            data: eventData,
            message: data.message || data.text || '',
          });
        }
        break;
      }

      case 'agent_thought': {
        // 处理思考事件 - 只传递给工作流回调，避免重复显示
        // 根据文档，提取正确的字段信息
        const toolInfo = {
          name: data.tool || '',
          input: data.tool_input || '{}',
          observation: data.observation || ''
        };
        
        // 根据文档，优先使用thought字段作为思考内容，如果没有则使用observation字段
        const thoughtContent = data.thought || data.observation || '';
        
        if (this.onWorkflowEventCallback) {
          this.onWorkflowEventCallback({
            event: 'agent_thought',
            data: data,
            message: thoughtContent,
            toolInfo: toolInfo
          });
        }
        // 根据经验教训，处理完agent_thought事件后必须立即返回，避免后续流程处理
        return;
      }

      case 'message_end': {
        // 不再传递空字符串，避免在UI中出现额外内容
        if (this.onWorkflowEventCallback) {
          this.onWorkflowEventCallback({
            event: 'message_end',
            data: data.data || {},
            message: data.message || data.text || '',
          });
        }
        // 确保通知流结束
        this.notifyEnd();
        break;
      }

      case 'ping':
        // 心跳事件，通常可以忽略
        break;

      case 'error':
        // 错误事件
        if (this.onErrorCallback) {
          this.onErrorCallback(new Error(data.message || 'Unknown error'));
        }
        break;

      case 'statistics':
        // 处理统计信息事件 - 传递给工作流事件回调
        if (this.onWorkflowEventCallback) {
          // 构建包含详细统计数据的消息
          let statisticsMessage = '统计信息已更新';
          if (data.data) {
            const statsData = data.data;
            const tokensInfo = statsData.total_tokens_estimated ? `，预计使用 tokens: ${statsData.total_tokens_estimated}` : '';
            const costInfo = statsData.estimated_cost ? `，预计费用: ${statsData.estimated_cost}` : '';
            statisticsMessage = `统计数据更新${tokensInfo}${costInfo}`;
          }
          this.onWorkflowEventCallback({
            event,
            data,
            message: statisticsMessage,
          });
        }
        break;

      default:
        // 其他未知事件 - 根据事件类型决定传递给哪个回调
        if (event && event === 'agent_thought') {
          // agent_thought事件应该传递给工作流事件回调，但不应该显示在工作流事件区域
          // 它应该只显示在思考过程区域
          if (this.onWorkflowEventCallback) {
            const toolInfo = {
              name: data.tool || '',
              input: data.tool_input || '{}',
              observation: data.observation || ''
            };
            
            const thoughtContent = data.thought || data.observation || '';
            
            this.onWorkflowEventCallback({
              event: 'agent_thought',
              data: data,
              message: thoughtContent,
              toolInfo: toolInfo
            });
          }
        }
        else if (event && (event.includes('workflow') || event.includes('node'))) {
          if (this.onWorkflowEventCallback) {
            // 对于工作流相关事件，传递完整的data对象，而不仅仅是data.data
            // 这样前端可以访问所有可能的字段
            this.onWorkflowEventCallback({
              event,
              // 对于workflow_finished等特殊事件，直接使用data
              // 对于其他事件，合并data和data.data，确保不丢失任何信息
              data: Object.assign({}, data, data.data || {}),
              message: data.message || data.text || data.thought || '',
            });
          }
        }
        else if (event && (event.startsWith('message') || event.startsWith('text') || event.startsWith('chunk') || event === 'agent_message')) {
          // 回复类事件应该传递给内容回调
          const possibleContent = data.text || data.data?.content || data.data?.text || data.answer || data.content || '';
          if (possibleContent) {
            if (this.onDataCallback) {
              this.onDataCallback(possibleContent, data);
            }
          }
        }
        else {
          // 其他事件不处理
        }
        break;
    }
  }

  /**
   * 通知流结束
   */
  public notifyEnd(): void {
    if (!this.finished) {
      this.finished = true;
      if (this.onCompleteCallback) {
        this.onCompleteCallback();
      }
    }
  }

  /**
   * 检查字符串是否包含可见字符
   * @param str 字符串
   * @returns 是否包含可见字符
   */
  private hasVisibleCharacters(str: string): boolean {
    for (let i = 0; i < str.length; i++) {
      const code = str.charCodeAt(i);
      // 可见字符范围：32-126 (ASCII 空格到 ~)
      // 以及扩展字符（大于127的字符）
      if ((code >= 32 && code <= 126) || code > 127) {
        return true;
      }
    }
    return false;
  }

  /**
   * 递归搜索对象中的所有可能的内容字段
   * @param obj 要搜索的对象
   * @returns 找到的内容字符串
   */
  private findContentInObject(obj: any): string {
    // 要搜索的内容字段列表 - 增强版本
    const contentFields = ['content', 'answer', 'text', 'message', 'output', 'value', 'result'];

    // 检查是否是对象
    if (!obj || typeof obj !== 'object') {
      return '';
    }

    // 尝试直接获取内容字段
    for (const field of contentFields) {
      if (obj[field] && typeof obj[field] === 'string' && obj[field].trim()) {
        return obj[field];
      }
    }

    // 检查常见的嵌套结构
    const nestedPaths = ['data', 'result', 'output', 'response', 'message', 'payload', 'body', 'result'];
    for (const path of nestedPaths) {
      if (obj[path] && typeof obj[path] === 'object') {
        const nestedContent = this.findContentInObject(obj[path]);
        if (nestedContent) {
          return nestedContent;
        }
      }
    }

    // 检查是否是简单对象（键值对）
    // 对于简单对象，如果只有一个键值对，且值是字符串，可以尝试返回该值
    const keys = Object.keys(obj);
    if (keys.length === 1 && typeof obj[keys[0]] === 'string' && obj[keys[0]].trim()) {
      return obj[keys[0]];
    }

    // 特殊处理：遍历所有键值对，寻找可能的内容
    for (const key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        const value = obj[key];
        if (typeof value === 'string' && value.trim() && !contentFields.includes(key.toLowerCase())) {
          // 检查是否是可能的内容（长度合理，不是纯数字或特殊格式）
          if (value.length > 3 && !/^\d+(?:\.\d+)?$/.test(value) && !value.startsWith('{') && !value.startsWith('[')) {
            return value;
          }
        }
      }
    }

    // 最后，如果什么都没找到，返回空字符串
    return '';
  }
}

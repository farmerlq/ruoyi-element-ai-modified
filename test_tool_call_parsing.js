// 测试工具调用数据解析
const testData = [
  {
    "id": "14583c52-683d-4405-883b-6a7cbd04b517",
    "tool": "",
    "event": "agent_thought",
    "file_id": null,
    "task_id": "8ba4b4ae-6733-4f4a-a9e9-17b714058fe6",
    "thought": "",
    "position": 1,
    "created_at": 1760593311,
    "tool_input": "",
    "observation": "",
    "message_files": [],
    "conversation_id": "11967d10-7cca-4c64-9108-7e55af51359c",
    "full_thought_content": ""
  },
  {
    "id": "14583c52-683d-4405-883b-6a7cbd04b517",
    "tool": "current_time",
    "event": "agent_thought",
    "file_id": null,
    "task_id": "8ba4b4ae-6733-4f4a-a9e9-17b714058fe6",
    "thought": "",
    "position": 1,
    "created_at": 1760593311,
    "tool_input": "{\"current_time\": {}}",
    "observation": "",
    "message_files": [],
    "conversation_id": "11967d10-7cca-4c64-9108-7e55af51359c",
    "full_thought_content": "\n\n[工具调用: current_time]\n参数: {\n  \"current_time\": {}\n}\n"
  },
  {
    "id": "14583c52-683d-4405-883b-6a7cbd04b517",
    "tool": "current_time",
    "event": "agent_thought",
    "file_id": null,
    "task_id": "8ba4b4ae-6733-4f4a-a9e9-17b714058fe6",
    "thought": "",
    "position": 1,
    "created_at": 1760593311,
    "tool_input": "{\"current_time\": {}}",
    "observation": "{\"current_time\": \"2025-10-16 05:41:52\"}",
    "message_files": [],
    "conversation_id": "11967d10-7cca-4c64-9108-7e55af51359c",
    "full_thought_content": "{\"current_time\": \"2025-10-16 05:41:52\"}\n\n[工具调用: current_time]\n参数: {\n  \"current_time\": {}\n}\n"
  },
  {
    "id": "b516a485-7901-4517-a731-1e598bb8dc8f",
    "tool": "",
    "event": "agent_thought",
    "file_id": null,
    "task_id": "8ba4b4ae-6733-4f4a-a9e9-17b714058fe6",
    "thought": "",
    "position": 2,
    "created_at": 1760593311,
    "tool_input": "",
    "observation": "",
    "message_files": [],
    "conversation_id": "11967d10-7cca-4c64-9108-7e55af51359c",
    "full_thought_content": ""
  },
  {
    "id": "b516a485-7901-4517-a731-1e598bb8dc8f",
    "tool": "dataset_1b8eeb90_2ac3_4dde_a280_3c79a70b7f61",
    "event": "agent_thought",
    "file_id": null,
    "task_id": "8ba4b4ae-6733-4f4a-a9e9-17b714058fe6",
    "thought": "",
    "position": 2,
    "created_at": 1760593311,
    "tool_input": "{\"dataset_1b8eeb90_2ac3_4dde_a280_3c79a70b7f61\": {\"query\": \"销售相关表结构\"}}",
    "observation": "",
    "message_files": [],
    "conversation_id": "11967d10-7cca-4c64-9108-7e55af51359c",
    "full_thought_content": "\n\n[工具调用: dataset_1b8eeb90_2ac3_4dde_a280_3c79a70b7f61]\n参数: {\n  \"dataset_1b8eeb90_2ac3_4dde_a280_3c79a70b7f61\": {\n    \"query\": \"销售相关表结构\"\n  }\n}\n"
  },
  {
    "id": "b516a485-7901-4517-a731-1e598bb8dc8f",
    "tool": "dataset_1b8eeb90_2ac3_4dde_a280_3c79a70b7f61",
    "event": "agent_thought",
    "file_id": null,
    "task_id": "8ba4b4ae-6733-4f4a-a9e9-17b714058fe6",
    "thought": "",
    "position": 2,
    "created_at": 1760593311,
    "tool_input": "{\"dataset_1b8eeb90_2ac3_4dde_a280_3c79a70b7f61\": {\"query\": \"销售相关表结构\"}}",
    "observation": "{\"dataset_1b8eeb90_2ac3_4dde_a280_3c79a70b7f61\": \"**Bill_SaleHeader   销售表**\n| ***\\\\*表名称\\\\****                                             | ***\\\\*Bill_SaleHeader Bill_SaleOrderHeader\\\\****               | ***\\\\*编号\\\\****      | ***\\\\*B_06\\\\**** | ***\\\\*日期\\\\****                                               | ***\\\\*2002/9/11\\\\**** |\n| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------- | -------------- | ------------------------------------------------------------ | ------------------- |\n| ***\\\\*No\\\\****                                                 | ***\\\\*字段名称\\\\****                                           | ***\\\\*字段类型\\\\****  | ***\\\\*空\\\\****   | ***\\\\*字段描述及备注\\\\****                                     |                     |\n| 0                                                            | SaleNo                                                       | VarChar(20)         |                | *****销售编号                                                |                     |\n| 1                                                            | SaleSeqID                                                    | Int                 |                | 销售小票号码0                                                |                     |\n| 2                                                            | SaleDateTime                                                 | datetime            | **√**          | 销售日期(GetDate())                                          |                     |\n| 3                                                            | SaleDepartID                                                 | VarChar(10)         | **√**          | 销售门店('')                                                 |                     |\n| 4                                                            | SaleType                                                     | Tinyint             |                | 销售类型（0） 0零售 1会员卡 2批发 3退货 4维修                |                     |\n| 5                                                            | ClientNo                                                     | VarChar(20)         | **√**          | 批发客户编号('')                                             |                     |\n| 6                                                            | CardNo                                                       | VarChar(20)         | **√**          | 会员卡号('')                                                 |                     |\n| 7                                                            | RefundmentBillNo                                             | VarChar(20)         | **√**          | 退货单号('')                                                 |                     |\n|                                                              |                                                              |                     |                |                                                              |                     |\n| 9                                                            | S_Number                                                     | Money               |                | 整单数量0                                                    |                     |\n| 10                                                           | S_MustTotal                                                  | Money               |                | 整单应付0 Price*Number                                       |                     |\n| 11                                                           | S_FactTotal                                                  | Money               |                | 整单实付0                                                    |                     |\n| 12                                                           | S_DiscTotal                                                  | Money               |                | 整单折扣合计0(含临时折扣)                                    |                     |\n| 13\n1.7. **业务数据表**\n\n1.6. **财务数据表**\n\"}",
    "message_files": [],
    "conversation_id": "11967d10-7cca-4c64-9108-7e55af51359c",
    "full_thought_content": "{\"dataset_1b8eeb90_2ac3_4dde_a280_3c79a70b7f61\": \"**Bill_SaleHeader   销售表**\n| ***\\\\*表名称\\\\****                                             | ***\\\\*Bill_SaleHeader Bill_SaleOrderHeader\\\\****               | ***\\\\*编号\\\\****      | ***\\\\*B_06\\\\**** | ***\\\\*日期\\\\****                                               | ***\\\\*2002/9/11\\\\**** |\n| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------- | -------------- | ------------------------------------------------------------ | ------------------- |\n| ***\\\\*No\\\\****                                                 | ***\\\\*字段名称\\\\****                                           | ***\\\\*字段类型\\\\****  | ***\\\\*空\\\\****   | ***\\\\*字段描述及备注\\\\****                                     |                     |\n| 0                                                            | SaleNo                                                       | VarChar(20)         |                | *****销售编号                                                |                     |\n| 1                                                            | SaleSeqID                                                    | Int                 |                | 销售小票号码0                                                |                     |\n| 2                                                            | SaleDateTime                                                 | datetime            | **√**          | 销售日期(GetDate())                                          |                     |\n| 3                                                            | SaleDepartID                                                 | VarChar(10)         | **√**          | 销售门店('')                                                 |                     |\n| 4                                                            | SaleType                                                     | Tinyint             |                | 销售类型（0） 0零售 1会员卡 2批发 3退货 4维修                |                     |\n| 5                                                            | ClientNo                                                     | VarChar(20)         | **√**          | 批发客户编号('')                                             |                     |\n| 6                                                            | CardNo                                                       | VarChar(20)         | **√**          | 会员卡号('')                                                 |                     |\n| 7                                                            | RefundmentBillNo                                             | VarChar(20)         | **√**          | 退货单号('')                                                 |                     |\n|                                                              |                                                              |                     |                |                                                              |                     |\n| 9                                                            | S_Number                                                     | Money               |                | 整单数量0                                                    |                     |\n| 10                                                           | S_MustTotal                                                  | Money               |                | 整单应付0 Price*Number                                       |                     |\n| 11                                                           | S_FactTotal                                                  | Money               |                | 整单实付0                                                    |                     |\n| 12                                                           | S_DiscTotal                                                  | Money               |                | 整单折扣合计0(含临时折扣)                                    |                     |\n| 13\n1.7. **业务数据表**\n\n1.6. **财务数据表**\n\"}

[工具调用: dataset_1b8eeb90_2ac3_4dde_a280_3c79a70b7f61]
参数: {
  \"dataset_1b8eeb90_2ac3_4dde_a280_3c79a70b7f61\": {
    \"query\": \"销售相关表结构\"
  }
}
"
  },
  {
    "id": "edcd68ee-0203-42cc-9242-3ae3371ac7c6",
    "tool": "",
    "event": "agent_thought",
    "file_id": null,
    "task_id": "8ba4b4ae-6733-4f4a-a9e9-17b714058fe6",
    "thought": "",
    "position": 3,
    "created_at": 1760593311,
    "tool_input": "",
    "observation": "",
    "message_files": [],
    "conversation_id": "11967d10-7cca-4c64-9108-7e55af51359c",
    "full_thought_content": ""
  }
];

// 按ID和position对数据进行分组
function groupToolCalls(data) {
  const grouped = {};
  
  data.forEach(item => {
    // 只处理有工具名称的事件
    if (item.tool) {
      const key = `${item.id}-${item.position}`;
      if (!grouped[key]) {
        grouped[key] = {
          id: item.id,
          tool: item.tool,
          event: item.event,
          position: item.position,
          tool_input: null,
          observation: null
        };
      }
      
      // 更新tool_input和observation（取非空值）
      if (item.tool_input && item.tool_input !== '{}') {
        grouped[key].tool_input = item.tool_input;
      }
      
      if (item.observation && item.observation !== '{}') {
        grouped[key].observation = item.observation;
      }
    }
  });
  
  return Object.values(grouped);
}

// 解析工具调用数据
function parseToolCalls(data) {
  const grouped = groupToolCalls(data);
  const toolCalls = [];
  
  grouped.forEach(item => {
    // 只有当工具名称存在时才添加
    if (item.tool) {
      toolCalls.push({
        name: item.tool,
        input: item.tool_input || '',
        observation: item.observation || ''
      });
    }
  });
  
  return toolCalls;
}

// 测试解析
const parsedToolCalls = parseToolCalls(testData);
console.log('解析出的工具调用:');
console.log(JSON.stringify(parsedToolCalls, null, 2));

// 验证每个工具调用是否包含必要的字段
parsedToolCalls.forEach((toolCall, index) => {
  console.log(`\n工具调用 ${index + 1}:`);
  console.log(`  名称: ${toolCall.name}`);
  console.log(`  输入: ${toolCall.input ? '存在' : '不存在'}`);
  console.log(`  响应: ${toolCall.observation ? '存在' : '不存在'}`);
  
  if (toolCall.observation) {
    try {
      const parsedObservation = JSON.parse(toolCall.observation);
      console.log(`  响应内容预览:`, JSON.stringify(parsedObservation).substring(0, 100) + '...');
    } catch (e) {
      console.log(`  响应内容预览:`, toolCall.observation.substring(0, 100) + '...');
    }
  }
});
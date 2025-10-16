import json

# 简化测试数据，只包含关键的工具调用事件
test_data = [
    # current_time 工具调用 - 有输入但没有响应
    {
        "tool": "current_time",
        "tool_input": "{\"current_time\": {}}",
        "observation": ""
    },
    # current_time 工具调用 - 有输入和响应
    {
        "tool": "current_time",
        "tool_input": "{\"current_time\": {}}",
        "observation": "{\"current_time\": \"2025-10-16 05:41:52\"}"
    },
    # dataset 工具调用 - 有输入但没有响应
    {
        "tool": "dataset_1b8eeb90_2ac3_4dde_a280_3c79a70b7f61",
        "tool_input": "{\"dataset_1b8eeb90_2ac3_4dde_a280_3c79a70b7f61\": {\"query\": \"销售相关表结构\"}}",
        "observation": ""
    },
    # dataset 工具调用 - 有输入和响应
    {
        "tool": "dataset_1b8eeb90_2ac3_4dde_a280_3c79a70b7f61",
        "tool_input": "{\"dataset_1b8eeb90_2ac3_4dde_a280_3c79a70b7f61\": {\"query\": \"销售相关表结构\"}}",
        "observation": "{\"dataset_1b8eeb90_2ac3_4dde_a280_3c79a70b7f61\": \"数据内容...\"}"
    }
]

def parse_tool_calls(data):
    """解析工具调用数据"""
    tool_calls = []
    
    # 按工具名称和输入分组，保留最新的响应
    tool_dict = {}
    
    for item in data:
        if item["tool"]:  # 只处理有工具名称的项
            key = f"{item['tool']}_{item['tool_input']}"
            if key not in tool_dict:
                tool_dict[key] = {
                    "name": item["tool"],
                    "input": item["tool_input"],
                    "observation": item["observation"]
                }
            elif item["observation"]:  # 如果有响应数据，则更新
                tool_dict[key]["observation"] = item["observation"]
    
    # 转换为列表
    for tool_call in tool_dict.values():
        tool_calls.append(tool_call)
    
    return tool_calls

# 测试解析
parsed_tool_calls = parse_tool_calls(test_data)
print('解析出的工具调用:')
print(json.dumps(parsed_tool_calls, indent=2, ensure_ascii=False))

print("\n详细分析:")
for i, tool_call in enumerate(parsed_tool_calls, 1):
    print(f"\n工具调用 {i}:")
    print(f"  工具名称: {tool_call['name']}")
    
    # 解析输入
    try:
        input_data = json.loads(tool_call['input'])
        print(f"  输入数据: {json.dumps(input_data, indent=2, ensure_ascii=False)}")
    except json.JSONDecodeError:
        print(f"  输入数据: {tool_call['input']}")
    
    # 解析响应
    if tool_call['observation']:
        try:
            observation_data = json.loads(tool_call['observation'])
            print(f"  响应数据: {json.dumps(observation_data, indent=2, ensure_ascii=False)}")
        except json.JSONDecodeError:
            print(f"  响应数据: {tool_call['observation']}")
    else:
        print("  响应数据: 无")
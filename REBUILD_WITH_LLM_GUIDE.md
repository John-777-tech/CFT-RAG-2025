# 使用LLM重新构建AbstractTree指南

## 问题说明

当前系统使用了Simple Hierarchy Strategy（基于pair_id顺序）建立层次关系，导致：
- 父节点和子节点之间没有语义关系
- Depth=2追溯父节点时引入了噪音
- 评估分数下降（MedQA下降90%+，DART下降34-60%）

## 解决方案：使用LLM建立语义层次关系

### 步骤1: 设置API Key

**选项1: 使用ARK API（推荐，默认）**
```bash
export ARK_API_KEY=your_ark_api_key
```

**选项2: 使用OpenAI API**
```bash
export OPENAI_API_KEY=your_openai_api_key
```

**选项3: 自定义API端点**
```bash
export OPENAI_API_KEY=your_key
export BASE_URL=https://your-api-endpoint.com
```

### 步骤2: 验证API Key设置

```bash
# 检查环境变量
echo $ARK_API_KEY
echo $OPENAI_API_KEY

# 或在Python中检查
python3 -c "import os; print('ARK_API_KEY:', '已设置' if os.environ.get('ARK_API_KEY') else '未设置')"
```

### 步骤3: 运行重建脚本

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
./rebuild_abstract_with_llm.sh
```

脚本会自动为所有3个数据集（MedQA, DART, TriviaQA）重新构建AbstractTree。

### 步骤4: 验证是否使用LLM

运行脚本时，应该看到类似以下的输出：
```
正在为文件 'default' 构建AbstractTree（1384 个abstracts）...
✓ 文件 'default' 的AbstractTree构建完成，包含 1384 个abstracts
```

**不应该看到**：
```
Warning: No API key found, using simple hierarchy strategy
```

### 步骤5: 重新运行Depth=2 Benchmark

重建完成后，重新运行depth=2 benchmark：

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 run_cuckoo_benchmark_depth2.py
```

## LLM建立层次关系的过程

当设置了API key后，系统会：

1. **将所有abstracts发送给LLM**
   - 限制每个abstract的内容长度为300字符（避免token过多）
   - 按照pair_id排序

2. **LLM分析层级关系**
   - 分析所有abstracts之间的语义关系
   - 建立有意义的层次结构
   - 返回父子关系（例如：`Abstract5 -> Abstract1` 或 `Abstract1 -> root`）

3. **构建AbstractTree**
   - 根据LLM返回的关系建立树结构
   - 父节点真正是对子节点的语义概括
   - 追溯父节点时能提供有价值的上下文

## 预期效果

使用LLM建立层次关系后：
- ✓ 父节点和子节点之间有语义联系
- ✓ 追溯父节点时能提供相关的上下文信息
- ✓ Depth=2的评估分数应该提升（至少不会下降90%+）

## 注意事项

1. **API调用成本**
   - LLM建立层次关系需要API调用
   - 每个文件的abstracts会发送一次API请求
   - 建议先测试一个小数据集

2. **API Rate Limit**
   - 如果abstracts数量很多，可能需要处理rate limit
   - 可以考虑分批处理或增加重试机制

3. **API响应格式**
   - 系统期望LLM返回特定格式：`Abstract{id} -> Abstract{parent_id}` 或 `Abstract{id} -> root`
   - 如果格式不对，会回退到simple strategy

## 故障排除

### 问题1: 仍然显示"Warning: No API key found"

**可能原因：**
- 环境变量未正确设置
- 脚本在子进程中运行，环境变量未传递

**解决方法：**
- 确认在同一个shell中设置并运行脚本
- 或使用 `env ARK_API_KEY=xxx ./rebuild_abstract_with_llm.sh`

### 问题2: API调用失败

**可能原因：**
- API key无效
- 网络连接问题
- API endpoint错误

**解决方法：**
- 检查API key是否正确
- 检查BASE_URL是否正确
- 查看日志文件（build_{dataset}_llm.log）

### 问题3: LLM返回格式错误

**可能原因：**
- LLM返回的格式不符合预期

**解决方法：**
- 系统会自动回退到simple strategy
- 检查日志确认LLM的响应格式


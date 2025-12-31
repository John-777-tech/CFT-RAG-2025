# 实体关系提取Prompt设计

## 核心Prompt模板

### 基础版本（3个实体）

```python
prompt = f"""请分析以下3个实体之间的层次关系（hierarchical relationships），并提取出依赖关系（dependency relationships）。

实体列表：
1. {entity1}
2. {entity2}
3. {entity3}

请分析这些实体之间的关系，重点关注以下类型的依赖关系：
1. **包含关系**（inclusion）：如 "A contains B" 或 "B belongs to A"
2. **分类关系**（categorization）：如 "A is a type of B" 或 "B is a category of A"
3. **组织关系**（organizational）：如 "A is part of B" 或 "B manages A"
4. **功能关系**（functional）：如 "A depends on B" 或 "B enables A"
5. **属性关系**（attribute）：如 "A is an attribute of B"

**重要规则**：
- 如果词修饰另一个名词，可以解释为子-父关系（child-parent relationship）
- 如果有连词（"and", "or"），将它们分组到同一父节点下
- 优先识别层次关系（hierarchical relationships），而不是简单的关联关系

请按照以下JSON格式返回结果：
```json
{{
  "relationships": [
    {{"child": "实体1", "parent": "实体2", "relation_type": "包含关系", "explanation": "简短说明"}},
    {{"child": "实体3", "parent": "实体1", "relation_type": "分类关系", "explanation": "简短说明"}}
  ],
  "root_entity": "根实体名称（如果有）",
  "reasoning": "简要说明你的分析过程"
}}
```

**注意**：
- 只返回确实存在的层次关系，不要创建虚假关系
- 如果实体之间没有明确的层次关系，可以返回空数组
- 确保每个关系都是 (子实体, 父实体) 的形式
"""
```

### 带上下文的版本

```python
prompt = f"""请分析以下3个实体之间的层次关系（hierarchical relationships），并提取出依赖关系（dependency relationships）。

实体列表：
1. {entity1}
2. {entity2}
3. {entity3}

上下文信息（帮助理解实体关系）：
{context_text}

请分析这些实体之间的关系，重点关注以下类型的依赖关系：
1. **包含关系**（inclusion）：如 "A contains B" 或 "B belongs to A"
2. **分类关系**（categorization）：如 "A is a type of B" 或 "B is a category of A"
3. **组织关系**（organizational）：如 "A is part of B" 或 "B manages A"
4. **功能关系**（functional）：如 "A depends on B" 或 "B enables A"
5. **属性关系**（attribute）：如 "A is an attribute of B"

**重要规则**：
- 如果词修饰另一个名词，可以解释为子-父关系（child-parent relationship）
- 如果有连词（"and", "or"），将它们分组到同一父节点下
- 优先识别层次关系（hierarchical relationships），而不是简单的关联关系
- 结合上下文信息，理解实体在特定领域中的关系

请按照以下JSON格式返回结果：
```json
{{
  "relationships": [
    {{"child": "实体1", "parent": "实体2", "relation_type": "包含关系", "explanation": "简短说明"}},
    {{"child": "实体3", "parent": "实体1", "relation_type": "分类关系", "explanation": "简短说明"}}
  ],
  "root_entity": "根实体名称（如果有）",
  "reasoning": "简要说明你的分析过程"
}}
```
"""
```

## 根据论文的关系类型

根据 `paper_revised.tex` 第48行，需要识别的关系类型包括：

1. **组织关系**（organizational）
2. **分类关系**（categorization）
3. **时间关系**（temporal）
4. **地理关系**（geographic）
5. **包含关系**（inclusion）
6. **功能关系**（functional）
7. **属性关系**（attribute）

重点关注表达依赖的关系，如：
- "belongs to"
- "contains"
- "is dependent on"

## 语法结构识别

根据论文第48行，关系可能通过以下语法结构表达：

- 名词短语（noun phrases）
- 介词短语（prepositional phrases）
- 关系从句（relative clauses）
- 同位语结构（appositive structures）

## 使用示例

### 示例1：基本用法

```python
from extract_entity_relationships_with_llm import extract_relationships_with_llm

entities = ["Python", "Programming Language", "Machine Learning"]
relationships = extract_relationships_with_llm(entities)

# 输出：
# [("Python", "Programming Language"), ("Machine Learning", "Programming Language")]
```

### 示例2：带上下文

```python
context = """
Python is a high-level programming language. 
Machine Learning is a subfield of artificial intelligence that uses programming languages like Python.
"""

entities = ["Python", "Programming Language", "Machine Learning"]
relationships = extract_relationships_with_llm(entities, context)
```

### 示例3：命令行使用

```bash
python extract_entity_relationships_with_llm.py \
    --entities "Python" "Programming Language" "Machine Learning" \
    --context ./context.txt \
    --output ./relationships.csv
```

## Prompt优化建议

### 1. 明确输出格式

要求LLM返回结构化的JSON，包含：
- `relationships`: 关系列表
- `relation_type`: 关系类型
- `explanation`: 关系说明
- `reasoning`: 分析过程

### 2. 提供示例

可以在prompt中添加few-shot示例：

```python
prompt += """
示例：
实体：["汽车", "交通工具", "发动机"]
关系：
- 汽车 -> 交通工具（分类关系：汽车是一种交通工具）
- 发动机 -> 汽车（包含关系：发动机是汽车的组成部分）
"""
```

### 3. 设置温度参数

```python
response = client.chat.completions.create(
    model=model_name,
    messages=[...],
    temperature=0.3,  # 降低温度以获得更一致的结果
)
```

### 4. 添加验证步骤

在解析结果后，验证：
- 实体是否匹配
- 关系是否合理
- 是否形成有效的层次结构

## 完整代码

已创建 `extract_entity_relationships_with_llm.py` 脚本，包含：
- ✅ 完整的prompt设计
- ✅ LLM调用逻辑
- ✅ 结果解析
- ✅ CSV保存功能
- ✅ 命令行接口

## 注意事项

1. **API配置**：确保设置了 `ARK_API_KEY` 或 `OPENAI_API_KEY`
2. **模型选择**：默认使用 `ge2.5-pro`，可通过 `MODEL_NAME` 环境变量修改
3. **Token限制**：如果上下文文本过长，需要截断
4. **错误处理**：如果LLM调用失败，有fallback机制


# Chunk提取说明

## 问题回答

### Chunk是数据集原本就包含的吗？

**不是**。Chunk是从数据集中的**文本字段提取/生成的**，而不是数据集原本就有的"chunk"字段。

## 数据集原始格式

### 1. AESLC数据集

**原始格式**：
```json
{
  "prompt": "Summarize the following email: ...",
  "answer": "邮件正文内容..."
}
```

**Chunk提取**：从 `answer` 或 `email_body` 字段提取

### 2. MedQA数据集

**原始格式**：
```json
{
  "question": "...",
  "answer": "答案文本..."
}
```

**Chunk提取**：从 `answer` 或 `expected_answer` 字段提取

### 3. DART数据集

**原始格式**：
```json
{
  "annotations": [{"text": "..."}],
  "answer": "..."
}
```

**Chunk提取**：优先从 `annotations[0].text` 提取，其次从 `answer` 字段提取

## Chunk提取过程

### 步骤1：从数据集读取文本字段

代码位置：`benchmark/build_medqa_dart_index.py` 和 `benchmark/build_aeslc_index.py`

```python
def extract_chunks_from_aeslc(dataset_path: str, max_samples: int = None) -> List[str]:
    """从AESLC数据集中提取chunks（邮件正文）"""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    chunks = []
    for item in dataset:
        # 从answer或email_body字段提取
        body = item.get('answer', item.get('email_body', ''))
        if body and len(body.strip()) > 0:
            chunks.append(body.strip())  # 每个answer作为一个chunk
    
    return chunks
```

### 步骤2：构建向量数据库

代码位置：`rag_base/build_index.py`

```python
def collect_chunks_from_file(file_path: str):
    """从文件收集chunks，支持.txt和.json文件"""
    if file_path.endswith('.json'):
        # 处理JSON文件
        data = json.load(file)
        for item in data:
            # 提取文本字段
            text_fields = ['answer', 'text', 'target', 'expected_answer']
            for field in text_fields:
                if field in item:
                    chunks.append(item[field].strip())
                    break
```

### 步骤3：保存为向量数据库

每个chunk（即每个数据项的文本字段）会被：
1. 转换为embedding向量
2. 存储到向量数据库中
3. 用于后续的相似度检索

## Chunk的定义

在这个项目中，**chunk = 数据集中的一个文本单元**：

- **AESLC**：每个邮件正文（`answer`字段）是一个chunk
- **MedQA**：每个答案（`answer`字段）是一个chunk
- **DART**：每个答案文本（`answer`或`annotations[0].text`）是一个chunk

## 数据流程

```
原始数据集（JSON格式）
    ↓
    ├─ 字段：prompt, answer, question, etc.
    │
    ↓ 提取文本字段
    │
Chunks列表（每个数据项的文本内容）
    ↓
    ├─ 转换为embedding
    │
    ↓ 存储到向量数据库
    │
向量数据库（VecDB）
    ↓
    ├─ 用于相似度检索
    │
    ↓
RAG检索和生成
```

## 关键代码位置

### 1. Chunk提取代码

- **AESLC**: `benchmark/build_aeslc_index.py` (第39-55行)
- **MedQA**: `benchmark/build_medqa_dart_index.py` (第39-55行)
- **DART**: `benchmark/build_medqa_dart_index.py` (第58-74行)
- **通用**: `rag_base/build_index.py` (第33-100行)

### 2. 向量数据库构建

- `rag_base/build_index.py` - `build_index_on_chunks()` 函数
- `rag_base/build_index.py` - `load_vec_db()` 函数

## 总结

1. **数据集原本不包含"chunk"字段**
2. **Chunk是从数据集的文本字段（如`answer`、`email_body`）中提取的**
3. **每个数据项的文本内容 = 一个chunk**
4. **Chunk提取是自动的**，在构建向量数据库时完成

## 示例

### AESLC数据集示例

**原始数据**：
```json
{
  "prompt": "Summarize the following email: ...",
  "answer": "Phillip, Could you please do me a favor?..."
}
```

**提取的Chunk**：
```
"Phillip, Could you please do me a favor?..."
```

这个chunk会被：
- 转换为embedding向量
- 存储到向量数据库
- 用于RAG检索




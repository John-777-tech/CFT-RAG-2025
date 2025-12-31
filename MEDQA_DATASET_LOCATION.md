# MedQA数据集位置说明

## 原始数据集位置

### 1. 原始文本数据（用于构建向量数据库）

**路径**：`/Users/zongyikun/Downloads/Med_data_clean/textbooks/en`

这是MedQA的原始文本数据目录，包含医学教科书文本文件。

**在代码中的使用**：
```python
# benchmark/run_benchmark.py 第44行
if vec_db_key == "medqa":
    data_source = "/Users/zongyikun/Downloads/Med_data_clean/textbooks/en"
```

### 2. 处理后的JSON数据集（用于benchmark）

**路径**：`/Users/zongyikun/Downloads/CFT-RAG-2025-main/datasets/processed/medqa.json`

这是处理后的MedQA数据集，包含question-answer对，用于运行benchmark。

**文件大小**：1.1MB

**格式**：
```json
[
  {
    "question": "...",
    "answer": "...",
    "expected_answer": "..."
  },
  ...
]
```

### 3. 提取的Chunks文件

**路径**：`/Users/zongyikun/Downloads/CFT-RAG-2025-main/datasets/medqa_chunks.txt`

这是从MedQA数据集中提取的chunks文本文件，用于构建向量数据库。

**文件大小**：52KB

## 数据流程

```
原始数据（Med_data_clean/textbooks/en）
    ↓
    ├─→ 提取chunks → medqa_chunks.txt
    │
    ├─→ 构建向量数据库 → vec_db_cache/medqa.db
    │
    └─→ 处理为JSON格式 → datasets/processed/medqa.json
         ↓
        用于benchmark测试
```

## 使用说明

### 1. 构建向量数据库

使用原始文本数据：
```bash
python benchmark/build_medqa_dart_index.py \
    --dataset-type medqa \
    --medqa-dataset ./datasets/processed/medqa.json
```

### 2. 运行Benchmark

使用处理后的JSON数据：
```bash
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/medqa.json \
    --vec-db-key medqa \
    --entities-file-name medqa_entities_file \
    --search-method 0 \
    --max-samples 100
```

## 文件位置总结

| 类型 | 路径 | 用途 |
|------|------|------|
| **原始文本数据** | `/Users/zongyikun/Downloads/Med_data_clean/textbooks/en` | 构建向量数据库的源数据 |
| **处理后的JSON** | `./datasets/processed/medqa.json` | Benchmark测试数据 |
| **Chunks文件** | `./datasets/medqa_chunks.txt` | 向量数据库构建的中间文件 |
| **向量数据库** | `./vec_db_cache/medqa.db` | 构建好的向量数据库 |
| **实体关系文件** | `./medqa_entities_file.csv` | 实体关系数据 |

## 注意事项

1. **原始数据路径**：`/Users/zongyikun/Downloads/Med_data_clean/textbooks/en` 是硬编码的绝对路径
2. **处理后的数据**：`./datasets/processed/medqa.json` 是相对路径，在项目目录下
3. **向量数据库**：首次运行时会自动构建，后续会直接加载缓存


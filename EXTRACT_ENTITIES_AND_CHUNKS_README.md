# 提取实体和Chunks脚本说明

## 概述

`benchmark/extract_entities_and_chunks.py` 是一个新的脚本，用于从数据集中提取实体和chunks，**但不构建实体树**。

此脚本结合了：
- **GitHub仓库的方法**：使用 `rag_base/build_index.py` 的方法提取和构建chunks
- **本地代码的方法**：使用正则表达式和共现关系提取实体

## 功能特点

### ✅ 提取Chunks（基于GitHub方法）

- 使用 `split_string_by_headings` 按标题分割文本
- 使用 `load_vec_db` 构建向量数据库
- 支持MedQA、DART、TriviaQA数据集

### ✅ 提取实体（使用spacy NER，与查询时方法一致）

- **默认使用spacy NER**提取实体（与查询时的方法一致）
- 自动选择合适的中文或英文spacy模型
- 如果spacy不可用，自动回退到正则表达式方法
- 使用共现关系建立实体关系
- 如果关系不足，使用基于长度的层级关系作为补充

### ❌ 不构建实体树

- **不调用** `build.build_forest`
- **不创建** EntityTree对象
- **不构建** Cuckoo Filter索引（如果search_method=7）

## 使用方法

### 基本用法

```bash
# 提取MedQA数据集
python benchmark/extract_entities_and_chunks.py \
    --dataset ./datasets/processed/medqa.json \
    --dataset-type medqa

# 提取DART数据集
python benchmark/extract_entities_and_chunks.py \
    --dataset ./datasets/processed/dart.json \
    --dataset-type dart

# 提取TriviaQA数据集
python benchmark/extract_entities_and_chunks.py \
    --dataset ./datasets/processed/triviaqa.json \
    --dataset-type triviaqa

# 自动检测数据集类型
python benchmark/extract_entities_and_chunks.py \
    --dataset ./datasets/processed/medqa.json \
    --dataset-type auto

# 使用spacy提取实体（默认）
python benchmark/extract_entities_and_chunks.py \
    --dataset ./datasets/processed/medqa.json \
    --dataset-type medqa \
    --use-spacy

# 不使用spacy，改用正则表达式
python benchmark/extract_entities_and_chunks.py \
    --dataset ./datasets/processed/medqa.json \
    --dataset-type medqa \
    --no-spacy
```

### 参数说明

- `--dataset`: 数据集JSON文件路径（必需）
- `--dataset-type`: 数据集类型（可选：`medqa`, `dart`, `triviaqa`, `auto`，默认：`auto`）
- `--output-dir`: 输出目录（默认：`./extracted_data`）
- `--max-samples`: 最大处理样本数（默认：`None`，处理全部）
- `--use-spacy`: 使用spacy NER提取实体（默认：`True`，与查询时方法一致）
- `--no-spacy`: 不使用spacy，改用正则表达式提取实体

### 输出文件

脚本会在输出目录生成以下文件：

1. **实体关系文件**: `{dataset_name}_entities.csv`
   - CSV格式：`子实体,父实体`
   - 示例：`Aortoiliac,Amlodipine`

2. **Chunks文件**: `{dataset_name}_chunks.txt`
   - 文本格式，每个chunk用 `# Chunk {i}` 标题分隔

3. **向量数据库**: `vec_db_cache/{dataset_name}.db`
   - 使用 `RagVecDB` 构建的向量数据库

## 与旧脚本的对比

### 旧脚本 (`benchmark/build_medqa_dart_index.py`)

- ✅ 提取chunks
- ✅ 提取实体
- ✅ 构建向量数据库
- ❌ **构建实体树**（调用 `build.build_forest`）

### 新脚本 (`benchmark/extract_entities_and_chunks.py`)

- ✅ 提取chunks（使用GitHub的方法）
- ✅ 提取实体（使用本地的方法）
- ✅ 构建向量数据库（使用GitHub的方法）
- ✅ **不构建实体树**

## 代码来源

### Chunks提取方法

来自GitHub仓库的 `rag_base/build_index.py`:
- `split_string_by_headings`
- `collect_chunks_from_file`
- `collect_chunks_from_dir`
- `load_vec_db`

### 实体提取方法

来自本地代码的 `benchmark/build_medqa_dart_index.py`:
- `extract_entities_simple`（正则表达式）
- `build_entities_file_*`（共现关系）

## 示例输出

```
================================================================================
提取 medqa 数据集的实体和chunks
================================================================================

步骤1: 提取chunks...
✓ 从MedQA数据集提取了 500 个chunks

步骤2: 保存chunks到文件...
✓ Chunks已保存到: ./extracted_data/medqa_chunks.txt

步骤3: 构建向量数据库 (key: medqa)...
注意：如果数据库已存在，将直接加载
✓ 向量数据库构建/加载完成

步骤4: 提取实体关系（不构建实体树）...
正在从数据集提取实体关系（数据集类型: medqa）...
使用正则表达式提取实体（从字段: answer）...
✓ 提取了 156 个唯一实体
创建基于共现关系的实体关系...
✓ 生成了 89 个实体关系
✓ 实体关系文件已保存到: ./extracted_data/medqa_entities.csv

================================================================================
✓ 提取完成！
================================================================================

输出文件:
  - 实体关系文件: ./extracted_data/medqa_entities.csv
  - Chunks文件: ./extracted_data/medqa_chunks.txt
  - 向量数据库: vec_db_cache/medqa.db

注意: 此脚本只提取实体和chunks，不构建实体树。
```

## 注意事项

1. **不构建实体树**：此脚本只提取实体和chunks，不调用 `build.build_forest`，因此不会创建EntityTree对象。

2. **向量数据库**：使用GitHub仓库的 `load_vec_db` 方法，会自动缓存到 `vec_db_cache/` 目录。

3. **实体关系**：使用简单的正则表达式和共现关系提取，可能不如手动标注准确。

4. **数据集格式**：需要JSON格式的数据集，包含 `answer` 或 `expected_answer` 字段。

## 后续使用

提取完成后，你可以：

1. **使用实体关系文件**：
   ```python
   # 手动构建实体树（如果需要）
   from trag_tree import build
   forest, nlp = build.build_forest(
       tree_num_max=50,
       entities_file_name="extracted_data/medqa_entities",
       search_method=1
   )
   ```

2. **使用向量数据库**：
   ```python
   from rag_base.build_index import load_vec_db
   db = load_vec_db("medqa", "extracted_data/medqa_chunks.txt")
   ```

3. **直接用于RAG**：
   - Baseline RAG（search_method=0）只需要向量数据库
   - Cuckoo Filter RAG（search_method=7）需要实体树


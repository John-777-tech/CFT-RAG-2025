# Benchmark数据集使用指南

本目录包含用于运行论文中提到的benchmark数据集的脚本。

## 支持的数据集

1. **MedQA** - 医学问答数据集
   - 来源: https://github.com/jind11/MedQA
   - 格式: JSONL文件

2. **AESLC** - 邮件摘要数据集
   - 来源: https://huggingface.co/datasets/Yale-LILY/aeslc
   - 格式: HuggingFace Dataset

3. **DART** - 数据到文本生成数据集
   - 来源: https://huggingface.co/datasets/dart
   - 格式: HuggingFace Dataset

## 使用步骤

### 1. 安装依赖

```bash
pip install datasets huggingface_hub
```

### 2. 下载和转换数据集

#### 方式A: 使用HuggingFace数据集 (AESLC, DART)

```bash
# 加载AESLC数据集
python benchmark/load_datasets.py --dataset aeslc

# 加载DART数据集
python benchmark/load_datasets.py --dataset dart

# 加载所有HuggingFace数据集
python benchmark/load_datasets.py --dataset all
```

#### 方式B: 手动下载MedQA

1. 从 https://github.com/jind11/MedQA 下载数据集
2. 解压到 `./datasets/MedQA/` 目录
3. 运行转换脚本:

```bash
python benchmark/load_datasets.py --dataset medqa --medqa-dir ./datasets/MedQA
```

转换后的数据集会保存在 `./datasets/processed/` 目录。

### 3. 运行Benchmark测试

```bash
# 使用MedQA数据集测试（限制10个样本用于快速测试）
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/medqa.json \
    --vec-db-key "test" \
    --tree-num-max 50 \
    --search-method 2 \
    --max-samples 10

# 使用AESLC数据集测试
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key "test" \
    --tree-num-max 50 \
    --search-method 2 \
    --max-samples 20

# 使用DART数据集测试
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/dart.json \
    --vec-db-key "test" \
    --tree-num-max 50 \
    --search-method 7 \
    --max-samples 20

# 完整测试（不使用--max-samples限制）
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/medqa.json \
    --vec-db-key "test" \
    --tree-num-max 50 \
    --search-method 2 \
    --output ./benchmark/results/medqa_full_results.json
```

## 搜索方法说明

- `0`: Vector Database Only
- `1`: Naive Tree-RAG
- `2`: Bloom Filter Search in Tree-RAG
- `5`: Improved Bloom Filter Search in Tree-RAG
- `7`: Cuckoo Filter in Tree-RAG (推荐，论文主要方法)
- `8`: Approximate Nearest Neighbors in Tree-RAG
- `9`: Approximate Nearest Neighbors in Graph-RAG

## 结果格式

测试结果保存为JSON格式，包含：
- `question`: 问题
- `answer`: 生成的回答
- `expected_answer`: 期望答案（如果有）
- `time`: 响应时间（秒）
- `answer_length`: 回答长度（字符数）

## 注意事项

1. 首次运行会从HuggingFace下载数据集，需要网络连接
2. MedQA数据集需要手动下载并放置到指定目录
3. 如果向量数据库尚未构建，需要先运行 `main.py` 构建索引
4. 建议先用 `--max-samples` 限制样本数量进行快速测试


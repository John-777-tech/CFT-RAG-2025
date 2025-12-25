# Benchmark数据集使用指南

## ✅ 已成功配置

✓ AESLC数据集已加载（1906条数据）
✓ 数据集位置：`./datasets/processed/aeslc.json`

## 🚀 快速开始

### 方式1: 快速测试（推荐，测试5条数据）

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
export HF_ENDPOINT=https://hf-mirror.com
export OPENAI_API_KEY=sk-busnzngzysfxwzlvyglfezgondkopwjmgqadfvtatrjeauvw
export BASE_URL=https://sr-endpoint.horay.ai/v1
export MODEL_NAME=ge2.5-pro

python benchmark/quick_test.py
```

### 方式2: 完整测试（使用更多数据）

```bash
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key "test" \
    --tree-num-max 50 \
    --search-method 2 \
    --max-samples 20 \
    --output ./benchmark/results/aeslc_results.json
```

## 📊 其他数据集

### MedQA（需要手动下载）

1. 从 https://github.com/jind11/MedQA 下载数据集
2. 解压到 `./datasets/MedQA/`
3. 运行转换：
```bash
python benchmark/load_datasets.py --dataset medqa --medqa-dir ./datasets/MedQA
```

### DART（HuggingFace，可能需要特殊配置）

```bash
python benchmark/load_datasets.py --dataset dart
```

## 📝 结果格式

测试结果包含：
- 问题 (question)
- 生成的回答 (answer)
- 响应时间 (time)
- 回答长度 (answer_length)

所有结果保存为JSON格式，便于后续分析。

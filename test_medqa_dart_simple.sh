#!/bin/bash
# 测试MedQA和DART数据集
# 比较Baseline (search_method=0) vs Tree-RAG (search_method=2)

export HF_ENDPOINT=https://hf-mirror.com
export ARK_API_KEY=af54be7c-7761-4c2b-96fb-369f28fde940
export BASE_URL=https://ark.cn-beijing.volces.com/api/v3
export MODEL_NAME=ep-20251221235820-5h6l2

PYTHONPATH=/Users/zongyikun/Downloads/CFT-RAG-2025-main
PYTHON=/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python

echo "================================================================"
echo "测试MedQA和DART数据集"
echo "比较 Baseline RAG (search_method=0) vs Tree-RAG (search_method=2)"
echo "================================================================"

# 测试MedQA - Baseline
echo ""
echo "1. MedQA Baseline (search_method=0)..."
$PYTHON benchmark/run_benchmark.py \
  --dataset ./datasets/processed/medqa.json \
  --vec-db-key medqa \
  --entities-file-name medqa_entities_file \
  --tree-num-max 50 \
  --search-method 0 \
  --output ./benchmark/results/medqa_baseline.json \
  --max-samples 50

# 测试MedQA - Tree-RAG
echo ""
echo "2. MedQA Tree-RAG (search_method=2)..."
$PYTHON benchmark/run_benchmark.py \
  --dataset ./datasets/processed/medqa.json \
  --vec-db-key medqa \
  --entities-file-name medqa_entities_file \
  --tree-num-max 50 \
  --search-method 2 \
  --output ./benchmark/results/medqa_treerag.json \
  --max-samples 50

# 测试DART - Baseline
echo ""
echo "3. DART Baseline (search_method=0)..."
$PYTHON benchmark/run_benchmark.py \
  --dataset ./datasets/processed/dart.json \
  --vec-db-key dart \
  --entities-file-name dart_entities_file \
  --tree-num-max 50 \
  --search-method 0 \
  --output ./benchmark/results/dart_baseline.json \
  --max-samples 50

# 测试DART - Tree-RAG
echo ""
echo "4. DART Tree-RAG (search_method=2)..."
$PYTHON benchmark/run_benchmark.py \
  --dataset ./datasets/processed/dart.json \
  --vec-db-key dart \
  --entities-file-name dart_entities_file \
  --tree-num-max 50 \
  --search-method 2 \
  --output ./benchmark/results/dart_treerag.json \
  --max-samples 50

echo ""
echo "================================================================"
echo "测试完成！"
echo "================================================================"

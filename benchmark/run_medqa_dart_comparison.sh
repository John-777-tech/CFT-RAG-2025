#!/bin/bash
# 完整测试脚本：比较MedQA和DART的Baseline vs Tree-RAG

export HF_ENDPOINT=https://hf-mirror.com
export ARK_API_KEY=af54be7c-7761-4c2b-96fb-369f28fde940
export BASE_URL=https://ark.cn-beijing.volces.com/api/v3
export MODEL_NAME=ep-20251221235820-5h6l2
export TOKENIZERS_PARALLELISM=false

PYTHONPATH=/Users/zongyikun/Downloads/CFT-RAG-2025-main
PYTHON=/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python

echo "================================================================================"
echo "MedQA和DART数据集对比测试"
echo "比较: Baseline RAG (search_method=0) vs Tree-RAG (search_method=2)"
echo "================================================================================"
echo ""

MAX_SAMPLES=${1:-50}  # 默认50个样本，可以通过参数指定

# MedQA测试
echo "================================================================================"
echo "1. MedQA Baseline (search_method=0)"
echo "================================================================================"
$PYTHON benchmark/run_benchmark.py \
  --dataset ./datasets/processed/medqa.json \
  --vec-db-key medqa \
  --entities-file-name medqa_entities_file \
  --tree-num-max 50 \
  --search-method 0 \
  --output ./benchmark/results/medqa_baseline.json \
  --max-samples $MAX_SAMPLES

echo ""
echo "================================================================================"
echo "2. MedQA Tree-RAG (search_method=2)"
echo "================================================================================"
$PYTHON benchmark/run_benchmark.py \
  --dataset ./datasets/processed/medqa.json \
  --vec-db-key medqa \
  --entities-file-name medqa_entities_file \
  --tree-num-max 50 \
  --search-method 2 \
  --output ./benchmark/results/medqa_treerag.json \
  --max-samples $MAX_SAMPLES

# DART测试（需要先构建DART向量数据库）
# 注意：DART可能使用MedQA的知识库，或者需要单独构建
echo ""
echo "================================================================================"
echo "3. DART Baseline (search_method=0)"
echo "================================================================================"
$PYTHON benchmark/run_benchmark.py \
  --dataset ./datasets/processed/dart.json \
  --vec-db-key medqa \
  --entities-file-name dart_entities_file \
  --tree-num-max 50 \
  --search-method 0 \
  --output ./benchmark/results/dart_baseline.json \
  --max-samples $MAX_SAMPLES

echo ""
echo "================================================================================"
echo "4. DART Tree-RAG (search_method=2)"
echo "================================================================================"
$PYTHON benchmark/run_benchmark.py \
  --dataset ./datasets/processed/dart.json \
  --vec-db-key medqa \
  --entities-file-name dart_entities_file \
  --tree-num-max 50 \
  --search-method 2 \
  --output ./benchmark/results/dart_treerag.json \
  --max-samples $MAX_SAMPLES

# 评估结果
echo ""
echo "================================================================================"
echo "评估结果"
echo "================================================================================"

for result_file in ./benchmark/results/medqa_baseline.json ./benchmark/results/medqa_treerag.json \
                   ./benchmark/results/dart_baseline.json ./benchmark/results/dart_treerag.json; do
  if [ -f "$result_file" ]; then
    echo ""
    echo "评估: $result_file"
    $PYTHON benchmark/evaluate_comprehensive.py \
      --results "$result_file" \
      --skip-bertscore
  fi
done

echo ""
echo "================================================================================"
echo "测试完成！"
echo "================================================================================"






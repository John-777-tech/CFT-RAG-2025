#!/bin/bash
# 在python310_arm环境中运行baseline RAG (search_method=0) benchmark

set -e

# 激活conda环境
source ~/opt/anaconda3/etc/profile.d/conda.sh
conda activate python310_arm

cd "$(dirname "$0")"

# 设置环境变量
export HF_ENDPOINT=https://hf-mirror.com

echo "=========================================="
echo "运行Baseline RAG Benchmark (search_method=0)"
echo "=========================================="
echo "Python环境: $(which python)"
echo "Python版本: $(python --version)"
echo ""

# 检查数据集是否存在
if [ ! -f "./datasets/processed/aeslc.json" ]; then
    echo "错误: 数据集文件不存在: ./datasets/processed/aeslc.json"
    exit 1
fi

echo "步骤 1/2: 运行Baseline Benchmark (search_method=0)"
echo "----------------------------------------"
echo "注意: 这将运行全部样本的benchmark（约1906个样本）"
echo "预计需要较长时间，支持断点续传"
echo ""

python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \
    --search-method 0 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --output ./benchmark/results/aeslc_baseline_rag_results.json \
    --checkpoint ./benchmark/results/aeslc_baseline_rag_results.json

if [ $? -ne 0 ]; then
    echo "错误: Benchmark运行失败"
    exit 1
fi

echo ""
echo "步骤 2/2: 计算评估指标 (ROUGE, BLEU, BERTScore)"
echo "----------------------------------------"
echo ""

python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/aeslc_baseline_rag_results.json \
    --output ./benchmark/results/aeslc_baseline_rag_evaluation.json

if [ $? -ne 0 ]; then
    echo "警告: 评估运行失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "完成！"
echo "=========================================="
echo ""
echo "查看结果:"
python -c "
import json
data = json.load(open('./benchmark/results/aeslc_baseline_rag_evaluation.json'))
print(f'总样本数: {data[\"total_samples\"]}')
print(f'\n平均分数:')
for k, v in data['average_scores'].items():
    print(f'  {k.upper()}: {v:.4f} ({v*100:.2f}%)')
"
echo ""
echo "结果文件:"
echo "  - Benchmark结果: ./benchmark/results/aeslc_baseline_rag_results.json"
echo "  - 评估结果: ./benchmark/results/aeslc_baseline_rag_evaluation.json"
echo ""


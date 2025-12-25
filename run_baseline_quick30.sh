#!/bin/bash
# 运行30个样本的baseline RAG快速测试

set -e

# 激活conda环境
source ~/opt/anaconda3/etc/profile.d/conda.sh
conda activate python310_arm

cd "$(dirname "$0")"

# 设置环境变量
export HF_ENDPOINT=https://hf-mirror.com
export TOKENIZERS_PARALLELISM=false

# 确保.env文件被加载（通过Python脚本）
echo "=========================================="
echo "Baseline RAG 快速测试 (30个样本)"
echo "=========================================="
echo ""

# 运行benchmark（run_benchmark.py会自动加载.env）
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \
    --search-method 0 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --output ./benchmark/results/aeslc_baseline_quick30.json \
    --checkpoint ./benchmark/results/aeslc_baseline_quick30.json \
    --max-samples 30

if [ $? -ne 0 ]; then
    echo "错误: Benchmark运行失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "运行评估指标"
echo "=========================================="
echo ""

python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/aeslc_baseline_quick30.json \
    --output ./benchmark/results/aeslc_baseline_quick30_evaluation.json

echo ""
echo "=========================================="
echo "评估结果"
echo "=========================================="
echo ""

python -c "
import json
data = json.load(open('./benchmark/results/aeslc_baseline_quick30_evaluation.json'))
print(f'总样本数: {data[\"total_samples\"]}')
print(f'\n平均分数:')
for k, v in data['average_scores'].items():
    print(f'  {k.upper()}: {v:.4f} ({v*100:.2f}%)')
"

echo ""
echo "结果文件:"
echo "  - Benchmark: ./benchmark/results/aeslc_baseline_quick30.json"
echo "  - 评估: ./benchmark/results/aeslc_baseline_quick30_evaluation.json"
echo ""


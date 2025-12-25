#!/bin/bash
# 在python310_arm环境中运行baseline RAG的评估

set -e

# 激活conda环境
source ~/opt/anaconda3/etc/profile.d/conda.sh
conda activate python310_arm

cd "$(dirname "$0")"

echo "=========================================="
echo "运行Baseline RAG评估 (python310_arm环境)"
echo "=========================================="
echo ""

# 检查结果文件是否存在
if [ ! -f "./benchmark/results/aeslc_full_benchmark.json" ]; then
    echo "错误: Benchmark结果文件不存在"
    echo "请先运行: python benchmark/run_benchmark.py --search-method 0 ..."
    exit 1
fi

echo "正在评估结果文件: ./benchmark/results/aeslc_full_benchmark.json"
echo ""

# 运行完整评估
python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/aeslc_full_benchmark.json \
    --output ./benchmark/results/aeslc_baseline_evaluation.json

echo ""
echo "=========================================="
echo "评估完成！"
echo "=========================================="
echo ""
echo "查看结果:"
python -c "
import json
data = json.load(open('./benchmark/results/aeslc_baseline_evaluation.json'))
print(f'总样本数: {data[\"total_samples\"]}')
print(f'\n平均分数:')
for k, v in data['average_scores'].items():
    print(f'  {k.upper()}: {v:.4f} ({v*100:.2f}%)')
"
echo ""



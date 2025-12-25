#!/bin/bash
# 运行AESLC数据集的baseline RAG benchmark并计算评估指标
# 参考 benchmark/BENCHMARK_GUIDE.md 的标准流程

set -e

cd "$(dirname "$0")"

echo "=========================================="
echo "运行AESLC Baseline RAG Benchmark"
echo "=========================================="
echo ""

# 检查数据集是否存在
if [ ! -f "./datasets/processed/aeslc.json" ]; then
    echo "错误: 数据集文件不存在: ./datasets/processed/aeslc.json"
    echo "请先运行: python benchmark/load_datasets.py --dataset aeslc"
    exit 1
fi

# 步骤1: 运行Benchmark (search_method=0, baseline RAG)
echo "步骤 1/2: 运行Baseline Benchmark (search_method=0)"
echo "----------------------------------------"
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \
    --search-method 0 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --output ./benchmark/results/aeslc_baseline_results.json \
    --checkpoint ./benchmark/results/aeslc_baseline_results.json \
    --max-samples 36

if [ $? -ne 0 ]; then
    echo "错误: Benchmark运行失败"
    exit 1
fi

echo ""
echo "步骤 2/2: 计算评估指标 (ROUGE, BLEU, BERTScore)"
echo "----------------------------------------"
python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/aeslc_baseline_results.json \
    --output ./benchmark/results/aeslc_baseline_evaluation.json

if [ $? -ne 0 ]; then
    echo "警告: 评估运行失败，但结果文件可能已生成"
    echo "如果BERTScore下载失败，可以添加 --skip-bertscore 参数跳过"
fi

echo ""
echo "=========================================="
echo "完成！"
echo "=========================================="
echo "结果文件:"
echo "  - Benchmark结果: ./benchmark/results/aeslc_baseline_results.json"
echo "  - 评估结果: ./benchmark/results/aeslc_baseline_evaluation.json"
echo ""
echo "查看评估结果:"
echo "  python -c \"import json; data=json.load(open('./benchmark/results/aeslc_baseline_evaluation.json')); print('总样本数:', data['total_samples']); [print(f'{k.upper()}: {v:.4f}') for k,v in data['average_scores'].items()]\""
echo ""

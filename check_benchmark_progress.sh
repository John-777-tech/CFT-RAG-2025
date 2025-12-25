#!/bin/bash
# 检查benchmark运行进度

cd "$(dirname "$0")"

echo "检查 AESLC Baseline vs Cuckoo Filter Benchmark 进度..."
echo ""

# 检查Baseline RAG进度
baseline_file="./benchmark/results/aeslc_baseline_comparison.json"
if [ -f "$baseline_file" ]; then
    count=$(python -c "import json; data=json.load(open('$baseline_file')); print(len(data))" 2>/dev/null || echo "0")
    echo "✓ Baseline RAG: $count/30 个样本已完成"
else
    echo "✗ Baseline RAG: 尚未开始"
fi

# 检查Cuckoo Filter进度
cuckoo_file="./benchmark/results/aeslc_cuckoo_comparison.json"
if [ -f "$cuckoo_file" ]; then
    count=$(python -c "import json; data=json.load(open('$cuckoo_file')); print(len(data))" 2>/dev/null || echo "0")
    echo "✓ Cuckoo Filter: $count/30 个样本已完成"
else
    echo "✗ Cuckoo Filter: 尚未开始"
fi

echo ""
echo "查看最新日志:"
tail -20 benchmark/results/aeslc_baseline_vs_cuckoo_run.log 2>/dev/null || echo "日志文件不存在"


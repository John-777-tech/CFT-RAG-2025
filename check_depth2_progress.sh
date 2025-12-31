#!/bin/bash
# 检查depth=2 benchmark的运行进度

cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

echo "=== Depth=2 Benchmark 运行状态 ==="
echo ""

# 检查进程
echo "运行中的进程:"
ps aux | grep "run_benchmark.py.*depth2\|run_cuckoo_benchmark_depth2" | grep -v grep
echo ""

# 检查结果文件
echo "结果文件:"
for dataset in medqa dart triviaqa; do
    file="benchmark/results/${dataset}_cuckoo_depth2.json"
    if [ -f "$file" ]; then
        count=$(jq 'length' "$file" 2>/dev/null || echo "0")
        size=$(ls -lh "$file" | awk '{print $5}')
        echo "  $dataset: $count 个样本 ($size)"
    else
        echo "  $dataset: 文件不存在"
    fi
done
echo ""

# 检查最新日志
echo "最新日志（如果有）:"
tail -20 benchmark/results/*depth2*.log 2>/dev/null | head -30

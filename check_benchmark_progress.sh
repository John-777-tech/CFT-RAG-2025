#!/bin/bash
# 检查benchmark运行进度

cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

echo "========================================"
echo "Benchmark运行进度检查"
echo "========================================"
echo ""

# 检查运行中的进程
RUNNING=$(ps aux | grep "run_benchmark.py" | grep -v grep | wc -l | tr -d ' ')
if [ "$RUNNING" -gt 0 ]; then
    echo "✓ 有 $RUNNING 个benchmark进程正在运行"
    ps aux | grep "run_benchmark.py" | grep -v grep | awk '{print "  PID:", $2, "运行:", $11, $12, $13, $14, $15}'
else
    echo "- 当前没有benchmark进程在运行"
fi

echo ""
echo "结果文件状态:"
echo ""

for dataset in medqa dart triviaqa; do
    for depth in 1 2; do
        file="benchmark/results/${dataset}_cuckoo_abstract_depth${depth}_100.json"
        if [ -f "$file" ]; then
            size=$(wc -l < "$file" 2>/dev/null || echo "0")
            mtime=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$file" 2>/dev/null || stat -c "%y" "$file" 2>/dev/null | cut -d' ' -f1-2)
            echo "  ✓ $dataset depth=$depth: $size 行, 修改时间: $mtime"
        else
            echo "  - $dataset depth=$depth: 文件不存在"
        fi
    done
done

echo ""
echo "查看最新日志: tail -50 benchmark_run.log"

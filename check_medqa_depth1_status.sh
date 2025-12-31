#!/bin/bash
# 检查MedQA Depth=1的运行状态

cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

echo "========================================"
echo "MedQA Depth=1 运行状态检查"
echo "========================================"
echo ""

# 检查进程
RUNNING=$(ps aux | grep "run_benchmark.py.*medqa.*depth.*1\|run_benchmark.py.*medqa.*--max-hierarchy-depth 1" | grep -v grep | wc -l | tr -d ' ')
if [ "$RUNNING" -gt 0 ]; then
    echo "✓ MedQA Depth=1 正在运行中"
    ps aux | grep "run_benchmark.py.*medqa.*depth.*1\|run_benchmark.py.*medqa.*--max-hierarchy-depth 1" | grep -v grep | awk '{print "  PID:", $2}'
else
    echo "- MedQA Depth=1 进程不在运行"
fi

echo ""
echo "结果文件状态:"
result_file="benchmark/results/medqa_cuckoo_abstract_depth1_100.json"
if [ -f "$result_file" ]; then
    count=$(python3 -c "import json; data=json.load(open('$result_file')); print(len(data) if isinstance(data, list) else 0)" 2>/dev/null || echo "0")
    echo "  ✓ 文件存在: $result_file"
    echo "  已完成: $count/100"
    if [ "$count" -eq 100 ]; then
        echo "  ✓ 实验已完成！"
    else
        echo "  ⏳ 实验进行中..."
    fi
else
    echo "  - 文件不存在（可能刚开始运行）"
fi

echo ""
echo "查看日志: tail -f medqa_depth1_run.log"


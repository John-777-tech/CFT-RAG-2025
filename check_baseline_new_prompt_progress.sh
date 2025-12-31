#!/bin/bash
# 检查Baseline新prompt实验的进度

cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

echo "=" | tr -d '\n' && echo "================================================================="
echo "Baseline新prompt实验进度检查"
echo "=" | tr -d '\n' && echo "================================================================="
echo ""

# 检查正在运行的进程
echo "正在运行的进程:"
RUNNING=$(ps aux | grep "run_benchmark.*search-method 0" | grep -v grep | wc -l | tr -d ' ')
if [ "$RUNNING" -gt 0 ]; then
    echo "  ✓ 有 $RUNNING 个Baseline实验正在运行"
    ps aux | grep "run_benchmark.*search-method 0" | grep -v grep | awk '{print "    PID: " $2 ", 命令: " $11 " " $12 " " $13 " " $14}'
else
    echo "  - 没有正在运行的Baseline实验"
fi
echo ""

# 检查结果文件
echo "结果文件状态:"
DATASETS=("medqa" "dart" "triviaqa")
MAX_SAMPLES=100

for DATASET in "${DATASETS[@]}"; do
    FILE="./benchmark/results/${DATASET}_baseline_new_prompt_${MAX_SAMPLES}.json"
    if [ -f "$FILE" ]; then
        LINE_COUNT=$(wc -l < "$FILE" 2>/dev/null | tr -d ' ' || echo "0")
        LAST_MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$FILE" 2>/dev/null || echo "N/A")
        
        # 尝试读取JSON并计算完成数量
        if command -v python3 &> /dev/null; then
            COMPLETED=$(python3 << EOF
import json
import os
try:
    with open("$FILE", 'r') as f:
        data = json.load(f)
    if isinstance(data, list):
        print(len(data))
    else:
        print("0")
except:
    print("0")
EOF
)
        else
            COMPLETED="N/A"
        fi
        
        if [ "$COMPLETED" != "0" ] && [ "$COMPLETED" != "N/A" ]; then
            echo "  ✓ ${DATASET}: ${COMPLETED}/${MAX_SAMPLES} 完成, 文件大小: $(ls -lh "$FILE" | awk '{print $5}'), 修改时间: ${LAST_MODIFIED}"
        else
            echo "  ⏳ ${DATASET}: 文件存在但可能为空或格式错误, 修改时间: ${LAST_MODIFIED}"
        fi
    else
        echo "  - ${DATASET}: 文件不存在"
    fi
done

echo ""
echo "=" | tr -d '\n' && echo "================================================================="




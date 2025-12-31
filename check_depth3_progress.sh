#!/bin/bash
# 检查depth=3实验的进度

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Depth=3 实验进度检查"
echo "=========================================="
echo ""

datasets=("medqa" "dart" "triviaqa")

for ds in "${datasets[@]}"; do
    result_file="benchmark/results/${ds}_cuckoo_abstract_depth3_100.json"
    
    ds_upper=$(echo $ds | tr '[:lower:]' '[:upper:]')
    echo "=== ${ds_upper} ==="
    
    if [ -f "$result_file" ]; then
        count=$(python3 -c "import json; f=open('$result_file'); data=json.load(f); print(len([x for x in data if 'error' not in x and x.get('answer', '') != '']))" 2>/dev/null || echo "0")
        total=$(python3 -c "import json; f=open('$result_file'); data=json.load(f); print(len(data))" 2>/dev/null || echo "0")
        echo "  进度: $count/$total 已完成"
        
        if [ "$count" -eq "$total" ] && [ "$total" -eq 100 ]; then
            echo "  状态: ✓ 完成"
        elif [ "$count" -gt 0 ]; then
            echo "  状态: ⚙️  运行中..."
        fi
    else
        echo "  状态: ⏳ 等待开始（文件不存在）"
    fi
    
    if ps aux | grep -q "run_benchmark.py.*${ds}.*depth3" | grep -v grep; then
        echo "  进程: ⚙️  正在运行"
    fi
    echo ""
done

echo "运行中的进程:"
ps aux | grep "run_benchmark.py" | grep "depth3" | grep -v grep || echo "  无"





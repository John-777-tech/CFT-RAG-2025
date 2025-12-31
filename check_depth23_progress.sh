#!/bin/bash
# 检查depth=2和depth=3实验的进度

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Depth=2 和 Depth=3 实验进度检查"
echo "=========================================="
echo ""

datasets=("medqa" "dart" "triviaqa")

for depth in 2 3; do
    echo "=== Depth=$depth ==="
    for ds in "${datasets[@]}"; do
        result_file="benchmark/results/${ds}_cuckoo_abstract_depth${depth}_100.json"
        log_file="benchmark/results/${ds}_cuckoo_abstract_depth${depth}_100_run.log"
        
        if [ -f "$result_file" ]; then
            # 使用Python检查JSON文件
            count=$(python3 -c "import json; f=open('$result_file'); data=json.load(f); print(len([x for x in data if 'error' not in x and x.get('answer', '') != '']))" 2>/dev/null || echo "0")
            total=$(python3 -c "import json; f=open('$result_file'); data=json.load(f); print(len(data))" 2>/dev/null || echo "0")
            echo "  $ds: $count/$total 已完成"
            
            # 检查是否有进程在运行
            if ps aux | grep -q "run_benchmark.py.*${ds}.*depth${depth}" | grep -v grep; then
                echo "    ⚙️  正在运行..."
            fi
        else
            echo "  $ds: 文件不存在"
        fi
    done
    echo ""
done

# 检查运行中的进程
echo "运行中的进程:"
ps aux | grep "run_benchmark.py" | grep -E "depth[23]" | grep -v grep || echo "  无"





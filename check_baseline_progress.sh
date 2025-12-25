#!/bin/bash
# 检查baseline benchmark运行进度

cd "$(dirname "$0")"

result_file="./benchmark/results/aeslc_baseline_rag_results.json"

if [ -f "$result_file" ]; then
    echo "检查benchmark进度..."
    count=$(python -c "import json; data=json.load(open('$result_file')); print(len(data))" 2>/dev/null || echo "0")
    echo "已完成样本数: $count / 36"
    
    if [ "$count" -ge 36 ]; then
        echo "✓ Benchmark已完成！"
        echo ""
        echo "运行评估..."
        source ~/opt/anaconda3/etc/profile.d/conda.sh
        conda activate python310_arm
        export HF_ENDPOINT=https://hf-mirror.com
        export TOKENIZERS_PARALLELISM=false
        
        python benchmark/evaluate_comprehensive.py \
            --results "$result_file" \
            --output ./benchmark/results/aeslc_baseline_rag_evaluation.json
        
        echo ""
        echo "评估结果:"
        python -c "
import json
data = json.load(open('./benchmark/results/aeslc_baseline_rag_evaluation.json'))
print(f'总样本数: {data[\"total_samples\"]}')
print(f'\n平均分数:')
for k, v in data['average_scores'].items():
    print(f'  {k.upper()}: {v:.4f} ({v*100:.2f}%)')
"
    else
        echo "Benchmark还在运行中，请稍候..."
    fi
else
    echo "结果文件不存在，benchmark可能还在初始化..."
fi



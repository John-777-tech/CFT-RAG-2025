#!/bin/bash
# 检查AESLC benchmark进度

cd "$(dirname "$0")"

echo "=========================================="
echo "AESLC Benchmark 进度检查"
echo "=========================================="
echo ""

# 检查Baseline RAG
if [ -f "./benchmark/results/aeslc_baseline_final.json" ]; then
    baseline_count=$(python -c "import json; data=json.load(open('./benchmark/results/aeslc_baseline_final.json', 'r', encoding='utf-8')); print(len(data))" 2>/dev/null || echo "0")
    echo "Baseline RAG: $baseline_count/30 样本完成"
    
    if [ -f "./benchmark/results/aeslc_baseline_final_evaluation.json" ]; then
        echo "  ✓ 评估已完成"
    else
        echo "  ⏳ 等待评估..."
    fi
else
    echo "Baseline RAG: 尚未开始"
fi

echo ""

# 检查Cuckoo Filter
if [ -f "./benchmark/results/aeslc_cuckoo_final.json" ]; then
    cuckoo_count=$(python -c "import json; data=json.load(open('./benchmark/results/aeslc_cuckoo_final.json', 'r', encoding='utf-8')); print(len(data))" 2>/dev/null || echo "0")
    echo "Cuckoo Filter: $cuckoo_count/30 样本完成"
    
    if [ -f "./benchmark/results/aeslc_cuckoo_final_evaluation.json" ]; then
        echo "  ✓ 评估已完成"
    else
        echo "  ⏳ 等待评估..."
    fi
else
    echo "Cuckoo Filter: 尚未开始"
fi

echo ""

# 检查报告
if [ -f "./benchmark/results/aeslc_baseline_vs_cuckoo_final_report.json" ]; then
    echo "=========================================="
    echo "✓ 对比报告已生成！"
    echo "=========================================="
    echo ""
    python -c "
import json
report = json.load(open('./benchmark/results/aeslc_baseline_vs_cuckoo_final_report.json', 'r', encoding='utf-8'))
baseline = report['baseline_rag']
cuckoo = report['cuckoo_filter']
comp = report['comparison']

print('【评估指标】')
print('-'*70)
print(f\"{'指标':<20} {'Baseline':<15} {'Cuckoo Filter':<15} {'差异':<10}\")
print('-'*70)
print(f\"{'ROUGE-1':<20} {baseline['metrics'].get('rouge1', 0):<15.4f} {cuckoo['metrics'].get('rouge1', 0):<15.4f} {comp['rouge1_diff']:+.4f}\")
print(f\"{'ROUGE-2':<20} {baseline['metrics'].get('rouge2', 0):<15.4f} {cuckoo['metrics'].get('rouge2', 0):<15.4f} {comp['rouge2_diff']:+.4f}\")
print(f\"{'ROUGE-L':<20} {baseline['metrics'].get('rougeL', 0):<15.4f} {cuckoo['metrics'].get('rougeL', 0):<15.4f} {comp['rougel_diff']:+.4f}\")
print(f\"{'BLEU':<20} {baseline['metrics'].get('bleu', 0):<15.4f} {cuckoo['metrics'].get('bleu', 0):<15.4f} {comp['bleu_diff']:+.4f}\")
print(f\"{'BERTScore F1':<20} {baseline['metrics'].get('bertscore', 0):<15.4f} {cuckoo['metrics'].get('bertscore', 0):<15.4f} {comp['bertscore_diff']:+.4f}\")
print()
print('【时间性能】')
print('-'*70)
print(f\"Baseline RAG平均时间: {baseline['avg_time']:.2f}秒\")
print(f\"Cuckoo Filter平均时间: {cuckoo['avg_time']:.2f}秒\")
print(f\"时间差异: {comp['time_diff']:+.2f}秒 ({comp['time_diff_pct']:+.2f}%)\")
"
else
    echo "⏳ 对比报告尚未生成"
fi

echo ""
echo "更新时间: $(date '+%Y-%m-%d %H:%M:%S')"





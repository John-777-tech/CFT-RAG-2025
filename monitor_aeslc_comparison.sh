#!/bin/bash
# 监控AESLC baseline vs cuckoo filter对比的进度

cd "$(dirname "$0")"

echo "监控AESLC Baseline RAG vs Cuckoo Filter对比进度..."
echo "按Ctrl+C停止监控"
echo ""

while true; do
    clear
    echo "=========================================="
    echo "AESLC Baseline vs Cuckoo Filter 进度监控"
    echo "=========================================="
    echo ""
    
    # 检查Baseline RAG进度
    if [ -f "./benchmark/results/aeslc_baseline_comparison.json" ]; then
        baseline_count=$(python -c "import json; data=json.load(open('./benchmark/results/aeslc_baseline_comparison.json', 'r', encoding='utf-8')); print(len(data))" 2>/dev/null || echo "0")
        echo "Baseline RAG: $baseline_count/30 样本完成"
        
        if [ -f "./benchmark/results/aeslc_baseline_comparison_evaluation.json" ]; then
            echo "  ✓ 评估已完成"
        else
            echo "  ⏳ 等待评估..."
        fi
    else
        echo "Baseline RAG: 尚未开始"
    fi
    
    echo ""
    
    # 检查Cuckoo Filter进度
    if [ -f "./benchmark/results/aeslc_cuckoo_comparison.json" ]; then
        cuckoo_count=$(python -c "import json; data=json.load(open('./benchmark/results/aeslc_cuckoo_comparison.json', 'r', encoding='utf-8')); print(len(data))" 2>/dev/null || echo "0")
        echo "Cuckoo Filter: $cuckoo_count/30 样本完成"
        
        if [ -f "./benchmark/results/aeslc_cuckoo_comparison_evaluation.json" ]; then
            echo "  ✓ 评估已完成"
        else
            echo "  ⏳ 等待评估..."
        fi
    else
        echo "Cuckoo Filter: 尚未开始"
    fi
    
    echo ""
    
    # 检查是否完成
    if [ -f "./benchmark/results/aeslc_baseline_vs_cuckoo_comparison_report.json" ]; then
        echo "=========================================="
        echo "✓ 对比完成！查看报告："
        echo "  ./benchmark/results/aeslc_baseline_vs_cuckoo_comparison_report.json"
        echo "=========================================="
        break
    fi
    
    echo "更新时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "按Ctrl+C停止监控"
    sleep 30
done


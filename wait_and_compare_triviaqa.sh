#!/bin/bash
# 等待TriviaQA Cuckoo Filter测试完成并对比结果

cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

RESULT_FILE="benchmark/results/triviaqa_cuckoo_50.json"
TARGET_SAMPLES=50

echo "=" | tr -d '\n' | head -c 80
echo ""
echo "⏳ 等待TriviaQA Cuckoo Filter测试完成..."
echo "=" | tr -d '\n' | head -c 80
echo ""

while true; do
    if [ -f "$RESULT_FILE" ]; then
        COUNT=$(python3 -c "import json; data=json.load(open('$RESULT_FILE')); print(len(data) if isinstance(data, list) else 0)" 2>/dev/null || echo "0")
        
        if [ "$COUNT" -ge "$TARGET_SAMPLES" ]; then
            echo ""
            echo "✅ 测试完成！($COUNT/$TARGET_SAMPLES 样本)"
            echo ""
            
            # 评估结果
            echo "正在评估Cuckoo Filter结果..."
            /Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python benchmark/evaluate_comprehensive.py \
                --results "$RESULT_FILE" \
                --output benchmark/results/triviaqa_cuckoo_50_evaluation.json
            
            # 对比结果
            echo ""
            echo "正在对比Baseline和Cuckoo Filter结果..."
            /Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python << 'PYEOF'
import json

print("=" * 80)
print("📊 TriviaQA Baseline vs Cuckoo Filter + Abstract 对比")
print("=" * 80)
print()

# 读取Baseline评估结果
baseline_file = "benchmark/results/triviaqa_baseline_50_evaluation.json"
with open(baseline_file, 'r', encoding='utf-8') as f:
    baseline = json.load(f)
baseline_scores = baseline.get('average_scores', {})

# 读取Cuckoo Filter评估结果
cuckoo_file = "benchmark/results/triviaqa_cuckoo_50_evaluation.json"
with open(cuckoo_file, 'r', encoding='utf-8') as f:
    cuckoo = json.load(f)
cuckoo_scores = cuckoo.get('average_scores', {})

# 显示对比表格
print(f"{'指标':<15} {'Baseline RAG':<18} {'Cuckoo Filter + Abstract':<25} {'差异':<15}")
print("-" * 73)

metrics = ['rouge1', 'rouge2', 'rougeL', 'bleu', 'bertscore']
metric_names = ['ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'BLEU', 'BERTScore']

for metric, name in zip(metrics, metric_names):
    baseline_val = baseline_scores.get(metric, 0)
    cuckoo_val = cuckoo_scores.get(metric, 0)
    diff = cuckoo_val - baseline_val
    diff_pct = (diff / baseline_val * 100) if baseline_val > 0 else 0
    
    diff_str = f"{diff:+.4f} ({diff_pct:+.1f}%)"
    print(f"{name:<15} {baseline_val:<18.4f} {cuckoo_val:<25.4f} {diff_str:<15}")

print()
print("=" * 80)
print("💡 说明:")
print("  • 正数差异表示Cuckoo Filter方法更好")
print("  • 负数差异表示Baseline方法更好")
print("=" * 80)
PYEOF
            
            break
        else
            echo "进度: $COUNT/$TARGET_SAMPLES 样本完成"
        fi
    else
        echo "等待结果文件生成..."
    fi
    
    sleep 30  # 每30秒检查一次
done


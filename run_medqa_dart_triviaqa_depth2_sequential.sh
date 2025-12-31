#!/bin/bash
# MedQA, DART, TriviaQA 100样本实验脚本 (depth=2)
# 顺序执行：先并行运行3个Baseline，完成后并行运行3个Cuckoo Filter Abstract

set -e

# 设置环境变量
export PYTHONPATH=/Users/zongyikun/Downloads/CFT-RAG-2025-main:$PYTHONPATH
export HF_ENDPOINT=https://hf-mirror.com  # 使用HuggingFace镜像
export MAX_HIERARCHY_DEPTH=2  # 设置层次回溯深度为2
PYTHON=/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MAX_SAMPLES=${1:-100}  # 默认100样本

datasets=(
    "medqa:./datasets/processed/medqa.json:medqa:medqa_entities_file"
    "dart:./datasets/processed/dart.json:dart:dart_entities_file"
    "triviaqa:./datasets/processed/triviaqa.json:triviaqa:triviaqa_entities_file"
)

echo "=========================================="
echo "Benchmark实验 (depth=2, ${MAX_SAMPLES}样本)"
echo "数据集: MedQA, DART, TriviaQA"
echo "执行模式: 顺序执行（先Baseline，后Cuckoo）"
echo "=========================================="
echo ""

# ========== 第一阶段：并行运行3个Baseline ==========
echo "=========================================="
echo "【阶段1/2】并行运行3个数据集的Baseline RAG"
echo "=========================================="
echo ""

baseline_pids=()

for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    dataset_upper=$(echo $dataset_name | tr '[:lower:]' '[:upper:]')
    
    echo "启动 ${dataset_upper} Baseline RAG..."
    
    "$PYTHON" benchmark/run_benchmark.py \
        --dataset "$dataset_file" \
        --vec-db-key "$vec_db_key" \
        --search-method 0 \
        --max-samples "$MAX_SAMPLES" \
        --output "benchmark/results/${dataset_name}_baseline_depth2_${MAX_SAMPLES}.json" \
        --entities-file-name "$entity_file" \
        > "benchmark/results/${dataset_name}_baseline_depth2_${MAX_SAMPLES}_run.log" 2>&1 &
    
    baseline_pids+=($!)
    echo "  → ${dataset_upper} Baseline 已启动 (PID: $!)"
    echo ""
done

echo "等待所有Baseline实验完成..."
echo "运行的进程: ${baseline_pids[*]}"
echo ""

# 等待所有Baseline完成
for pid in "${baseline_pids[@]}"; do
    wait $pid
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "✓ 进程 $pid 完成"
    else
        echo "⚠ 进程 $pid 异常退出 (code: $exit_code)"
    fi
done

echo ""
echo "=========================================="
echo "✓ 所有Baseline实验已完成"
echo "=========================================="
echo ""

# ========== 第二阶段：并行运行3个Cuckoo Filter Abstract ==========
echo "=========================================="
echo "【阶段2/2】并行运行3个数据集的Cuckoo Filter Abstract RAG"
echo "=========================================="
echo ""

cuckoo_pids=()

for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    dataset_upper=$(echo $dataset_name | tr '[:lower:]' '[:upper:]')
    
    echo "启动 ${dataset_upper} Cuckoo Filter Abstract RAG (depth=2)..."
    
    "$PYTHON" benchmark/run_benchmark.py \
        --dataset "$dataset_file" \
        --vec-db-key "$vec_db_key" \
        --search-method 7 \
        --max-samples "$MAX_SAMPLES" \
        --output "benchmark/results/${dataset_name}_cuckoo_abstract_depth2_${MAX_SAMPLES}.json" \
        --entities-file-name "$entity_file" \
        > "benchmark/results/${dataset_name}_cuckoo_abstract_depth2_${MAX_SAMPLES}_run.log" 2>&1 &
    
    cuckoo_pids+=($!)
    echo "  → ${dataset_upper} Cuckoo 已启动 (PID: $!)"
    echo ""
done

echo "等待所有Cuckoo Filter Abstract实验完成..."
echo "运行的进程: ${cuckoo_pids[*]}"
echo ""

# 等待所有Cuckoo完成
for pid in "${cuckoo_pids[@]}"; do
    wait $pid
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "✓ 进程 $pid 完成"
    else
        echo "⚠ 进程 $pid 异常退出 (code: $exit_code)"
    fi
done

echo ""
echo "=========================================="
echo "✓ 所有Cuckoo Filter Abstract实验已完成"
echo "=========================================="
echo ""

# ========== 评估阶段 ==========
echo "=========================================="
echo "【评估阶段】对所有结果进行评估"
echo "=========================================="
echo ""

for dataset_info in "${datasets[@]}"; do
    IFS=':' read -r dataset_name dataset_file vec_db_key entity_file <<< "$dataset_info"
    dataset_upper=$(echo $dataset_name | tr '[:lower:]' '[:upper:]')
    
    echo "评估 ${dataset_upper} Baseline结果..."
    "$PYTHON" benchmark/evaluate_comprehensive.py \
        --results "benchmark/results/${dataset_name}_baseline_depth2_${MAX_SAMPLES}.json" \
        --output "benchmark/results/${dataset_name}_baseline_depth2_${MAX_SAMPLES}_evaluation.json" \
        2>&1 | tail -10
    echo ""
    
    echo "评估 ${dataset_upper} Cuckoo Filter结果..."
    "$PYTHON" benchmark/evaluate_comprehensive.py \
        --results "benchmark/results/${dataset_name}_cuckoo_abstract_depth2_${MAX_SAMPLES}.json" \
        --output "benchmark/results/${dataset_name}_cuckoo_abstract_depth2_${MAX_SAMPLES}_evaluation.json" \
        2>&1 | tail -10
    echo ""
done

# ========== 生成对比报告 ==========
echo "=========================================="
echo "生成对比报告..."
echo "=========================================="
"$PYTHON" << 'EOF'
import json
import os

max_samples = "100"
depth = "2"

print("=" * 110)
print(f"所有Benchmark数据集完整评估报告汇总（depth={depth}，上下回溯{depth}级）")
print("=" * 110)

datasets_config = [
    ('medqa', 'MedQA'),
    ('dart', 'DART'),
    ('triviaqa', 'TriviaQA')
]

results = {}

for dataset_key, dataset_name in datasets_config:
    bl_file = f'benchmark/results/{dataset_key}_baseline_depth2_{max_samples}.json'
    ck_file = f'benchmark/results/{dataset_key}_cuckoo_abstract_depth2_{max_samples}.json'
    bl_eval = f'benchmark/results/{dataset_key}_baseline_depth2_{max_samples}_evaluation.json'
    ck_eval = f'benchmark/results/{dataset_key}_cuckoo_abstract_depth2_{max_samples}_evaluation.json'
    
    if all(os.path.exists(f) for f in [bl_file, ck_file, bl_eval, ck_eval]):
        with open(bl_file, 'r') as f:
            bl_data = json.load(f)
        with open(ck_file, 'r') as f:
            ck_data = json.load(f)
        with open(bl_eval, 'r') as f:
            bl_eval_data = json.load(f)
        with open(ck_eval, 'r') as f:
            ck_eval_data = json.load(f)
        
        if len(bl_data) == int(max_samples) and len(ck_data) == int(max_samples):
            results[dataset_name] = {
                'baseline': {
                    'scores': bl_eval_data.get('average_scores', {}),
                    'times': [x.get('time', 0) for x in bl_data if 'time' in x and x.get('time', 0) > 0 and 'error' not in x]
                },
                'cuckoo': {
                    'scores': ck_eval_data.get('average_scores', {}),
                    'times': [x.get('time', 0) for x in ck_data if 'time' in x and x.get('time', 0) > 0 and 'error' not in x]
                }
            }

# 生成汇总表
print("\n【评估分数对比汇总（depth={}）】".format(depth))
print("=" * 110)
print(f"\n{'数据集':<12} {'方法':<35} {'ROUGE-L':<12} {'BLEU':<12} {'BERTScore':<12} {'ROUGE-L提升':<15} {'BLEU提升':<15}")
print("-" * 110)

for dataset_name in ['MedQA', 'DART', 'TriviaQA']:
    if dataset_name in results:
        data = results[dataset_name]
        bl = data['baseline']
        ck = data['cuckoo']
        
        bl_rougeL = bl['scores'].get('rougeL', 0)
        ck_rougeL = ck['scores'].get('rougeL', 0)
        bl_bleu = bl['scores'].get('bleu', 0)
        ck_bleu = ck['scores'].get('bleu', 0)
        bl_bert = bl['scores'].get('bertscore', bl['scores'].get('bertscore_f1', 0))
        ck_bert = ck['scores'].get('bertscore', ck['scores'].get('bertscore_f1', 0))
        
        rouge_improve = ((ck_rougeL - bl_rougeL) / bl_rougeL * 100) if bl_rougeL > 0 else 0
        bleu_improve = ((ck_bleu - bl_bleu) / bl_bleu * 100) if bl_bleu > 0 else 0
        
        print(f"{dataset_name:<12} {'Baseline RAG':<35} {bl_rougeL:<12.4f} {bl_bleu:<12.4f} {bl_bert:<12.4f} {'-':<15} {'-':<15}")
        print(f"{'':<12} {'Cuckoo Abstract RAG (depth=' + depth + ')':<35} {ck_rougeL:<12.4f} {ck_bleu:<12.4f} {ck_bert:<12.4f} {'+'+str(rouge_improve)+'%':<15} {'+'+str(bleu_improve)+'%':<15}")
        print("-" * 110)

# 时间性能汇总
print("\n\n【时间性能对比汇总（depth={}）】".format(depth))
print("=" * 110)
print(f"\n{'数据集':<12} {'方法':<35} {'平均耗时(秒)':<18} {'总耗时(分钟)':<18} {'速度变化':<15}")
print("-" * 110)

for dataset_name in ['MedQA', 'DART', 'TriviaQA']:
    if dataset_name in results:
        data = results[dataset_name]
        bl = data['baseline']
        ck = data['cuckoo']
        
        if bl['times'] and ck['times']:
            bl_avg = sum(bl['times']) / len(bl['times'])
            ck_avg = sum(ck['times']) / len(ck['times'])
            bl_total = sum(bl['times']) / 60
            ck_total = sum(ck['times']) / 60
            
            speed_change = ((ck_avg - bl_avg) / bl_avg * 100) if bl_avg > 0 else 0
            speed_label = f"{speed_change:+.1f}%" if speed_change < 0 else f"+{speed_change:.1f}%"
            speed_desc = "更快" if speed_change < 0 else "更慢"
            
            print(f"{dataset_name:<12} {'Baseline RAG':<35} {bl_avg:<18.2f} {bl_total:<18.2f} {'-':<15}")
            print(f"{'':<12} {'Cuckoo Abstract RAG (depth=' + depth + ')':<35} {ck_avg:<18.2f} {ck_total:<18.2f} {speed_label+'('+speed_desc+')':<15}")
            print("-" * 110)

# 检索时间对比
print("\n\n【检索时间对比汇总（depth={}）】".format(depth))
print("=" * 110)
print(f"\n{'数据集':<12} {'方法':<35} {'平均检索时间(秒)':<20} {'平均生成时间(秒)':<20}")
print("-" * 110)

for dataset_name in ['MedQA', 'DART', 'TriviaQA']:
    if dataset_name in results:
        dataset_key = dataset_name.lower()
        bl_file = f'benchmark/results/{dataset_key}_baseline_depth2_{max_samples}.json'
        ck_file = f'benchmark/results/{dataset_key}_cuckoo_abstract_depth2_{max_samples}.json'
        
        if os.path.exists(bl_file):
            with open(bl_file, 'r') as f:
                bl_data = json.load(f)
            bl_retrieval_times = [x.get('retrieval_time', 0) for x in bl_data if 'retrieval_time' in x and x.get('retrieval_time', 0) > 0 and 'error' not in x]
            bl_generation_times = [x.get('generation_time', 0) for x in bl_data if 'generation_time' in x and x.get('generation_time', 0) > 0 and 'error' not in x]
            
            if bl_retrieval_times and bl_generation_times:
                bl_avg_retrieval = sum(bl_retrieval_times) / len(bl_retrieval_times)
                bl_avg_generation = sum(bl_generation_times) / len(bl_generation_times)
                
                if os.path.exists(ck_file):
                    with open(ck_file, 'r') as f:
                        ck_data = json.load(f)
                    ck_retrieval_times = [x.get('retrieval_time', 0) for x in ck_data if 'retrieval_time' in x and x.get('retrieval_time', 0) > 0 and 'error' not in x]
                    ck_generation_times = [x.get('generation_time', 0) for x in ck_data if 'generation_time' in x and x.get('generation_time', 0) > 0 and 'error' not in x]
                    
                    if ck_retrieval_times and ck_generation_times:
                        ck_avg_retrieval = sum(ck_retrieval_times) / len(ck_retrieval_times)
                        ck_avg_generation = sum(ck_generation_times) / len(ck_generation_times)
                        
                        print(f"{dataset_name:<12} {'Baseline RAG':<35} {bl_avg_retrieval:<20.3f} {bl_avg_generation:<20.2f}")
                        print(f"{'':<12} {'Cuckoo Abstract RAG (depth=' + depth + ')':<35} {ck_avg_retrieval:<20.3f} {ck_avg_generation:<20.2f}")
                        print("-" * 110)

print("\n" + "=" * 110)
EOF

echo ""
echo "=========================================="
echo "✓ 所有实验和评估完成！"
echo "=========================================="


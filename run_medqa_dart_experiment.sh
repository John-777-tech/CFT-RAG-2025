#!/bin/bash
# 运行MedQA和DART的Baseline RAG vs Cuckoo Filter Abstract RAG对比实验

export HF_ENDPOINT=https://hf-mirror.com
export ARK_API_KEY=af54be7c-7761-4c2b-96fb-369f28fde940
export BASE_URL=https://ark.cn-beijing.volces.com/api/v3
export MODEL_NAME=ep-20251221235820-5h6l2
export TOKENIZERS_PARALLELISM=false

PYTHONPATH=/Users/zongyikun/Downloads/CFT-RAG-2025-main
PYTHON=/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python

# 获取样本数量参数，默认为20
MAX_SAMPLES=${1:-20}

echo "================================================================================"
echo "MedQA和DART对比实验：Baseline RAG vs Cuckoo Filter Abstract RAG"
echo "样本数量: $MAX_SAMPLES"
echo "================================================================================"
echo ""

# 检查向量数据库是否存在
if [ ! -d "vec_db_cache/medqa.db" ] && [ ! -d "vec_db_cache/dart.db" ]; then
    echo "警告: 向量数据库可能不存在，请先运行构建脚本："
    echo "  python benchmark/build_medqa_dart_index.py --dataset-type both"
    echo ""
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# MedQA测试
echo "================================================================================"
echo "1. MedQA Baseline RAG (search_method=0)"
echo "================================================================================"
echo ""
$PYTHON benchmark/run_benchmark.py \
  --dataset ./datasets/processed/medqa.json \
  --vec-db-key medqa \
  --entities-file-name medqa_entities_file \
  --tree-num-max 50 \
  --search-method 0 \
  --output ./benchmark/results/medqa_baseline.json \
  --max-samples $MAX_SAMPLES

echo ""
echo "================================================================================"
echo "2. MedQA Cuckoo Filter Abstract RAG (search_method=7)"
echo "================================================================================"
echo ""
$PYTHON benchmark/run_benchmark.py \
  --dataset ./datasets/processed/medqa.json \
  --vec-db-key medqa \
  --entities-file-name medqa_entities_file \
  --tree-num-max 50 \
  --search-method 7 \
  --output ./benchmark/results/medqa_cuckoo_abstract.json \
  --max-samples $MAX_SAMPLES

# DART测试
echo ""
echo "================================================================================"
echo "3. DART Baseline RAG (search_method=0)"
echo "================================================================================"
echo ""
$PYTHON benchmark/run_benchmark.py \
  --dataset ./datasets/processed/dart.json \
  --vec-db-key dart \
  --entities-file-name dart_entities_file \
  --tree-num-max 50 \
  --search-method 0 \
  --output ./benchmark/results/dart_baseline.json \
  --max-samples $MAX_SAMPLES

echo ""
echo "================================================================================"
echo "4. DART Cuckoo Filter Abstract RAG (search_method=7)"
echo "================================================================================"
echo ""
$PYTHON benchmark/run_benchmark.py \
  --dataset ./datasets/processed/dart.json \
  --vec-db-key dart \
  --entities-file-name dart_entities_file \
  --tree-num-max 50 \
  --search-method 7 \
  --output ./benchmark/results/dart_cuckoo_abstract.json \
  --max-samples $MAX_SAMPLES

# 评估结果
echo ""
echo "================================================================================"
echo "评估结果"
echo "================================================================================"
echo ""

for result_file in ./benchmark/results/medqa_baseline.json ./benchmark/results/medqa_cuckoo_abstract.json \
                   ./benchmark/results/dart_baseline.json ./benchmark/results/dart_cuckoo_abstract.json; do
  if [ -f "$result_file" ]; then
    echo ""
    echo "评估: $(basename $result_file)"
    $PYTHON benchmark/evaluate_comprehensive.py \
      --results "$result_file" \
      --skip-bertscore \
      --output "${result_file%.json}_evaluation.json" 2>&1 | tail -20
  fi
done

# 打印对比总结
echo ""
echo "================================================================================"
echo "对比总结"
echo "================================================================================"
echo ""

$PYTHON << 'PYEOF'
import json
import os

def load_eval(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None

print("\n=== MedQA对比 ===")
medqa_baseline = load_eval('./benchmark/results/medqa_baseline_evaluation.json')
medqa_cuckoo = load_eval('./benchmark/results/medqa_cuckoo_abstract_evaluation.json')

if medqa_baseline and medqa_cuckoo:
    bl = medqa_baseline['average_scores']
    ck = medqa_cuckoo['average_scores']
    print(f"Baseline:")
    print(f"  ROUGE-L: {bl.get('rougeL', 0):.4f}")
    print(f"  BLEU: {bl.get('bleu', 0):.4f}")
    print(f"Cuckoo+Abstract:")
    print(f"  ROUGE-L: {ck.get('rougeL', 0):.4f}")
    print(f"  BLEU: {ck.get('bleu', 0):.4f}")
    rouge_diff = ck.get('rougeL', 0) - bl.get('rougeL', 0)
    bleu_diff = ck.get('bleu', 0) - bl.get('bleu', 0)
    print(f"提升:")
    print(f"  ROUGE-L: {rouge_diff:+.4f} ({rouge_diff*100/max(bl.get('rougeL', 0.001), 0.001):.2f}%)")
    print(f"  BLEU: {bleu_diff:+.4f} ({bleu_diff*100/max(bl.get('bleu', 0.001), 0.001):.2f}%)")

print("\n=== DART对比 ===")
dart_baseline = load_eval('./benchmark/results/dart_baseline_evaluation.json')
dart_cuckoo = load_eval('./benchmark/results/dart_cuckoo_abstract_evaluation.json')

if dart_baseline and dart_cuckoo:
    bl = dart_baseline['average_scores']
    ck = dart_cuckoo['average_scores']
    print(f"Baseline:")
    print(f"  ROUGE-L: {bl.get('rougeL', 0):.4f}")
    print(f"  BLEU: {bl.get('bleu', 0):.4f}")
    print(f"Cuckoo+Abstract:")
    print(f"  ROUGE-L: {ck.get('rougeL', 0):.4f}")
    print(f"  BLEU: {ck.get('bleu', 0):.4f}")
    rouge_diff = ck.get('rougeL', 0) - bl.get('rougeL', 0)
    bleu_diff = ck.get('bleu', 0) - bl.get('bleu', 0)
    print(f"提升:")
    print(f"  ROUGE-L: {rouge_diff:+.4f} ({rouge_diff*100/max(bl.get('rougeL', 0.001), 0.001):.2f}%)")
    print(f"  BLEU: {bleu_diff:+.4f} ({bleu_diff*100/max(bl.get('bleu', 0.001), 0.001):.2f}%)")

PYEOF

echo ""
echo "================================================================================"
echo "实验完成！"
echo "================================================================================"
echo ""
echo "结果文件："
echo "  - MedQA Baseline: ./benchmark/results/medqa_baseline.json"
echo "  - MedQA Cuckoo+Abstract: ./benchmark/results/medqa_cuckoo_abstract.json"
echo "  - DART Baseline: ./benchmark/results/dart_baseline.json"
echo "  - DART Cuckoo+Abstract: ./benchmark/results/dart_cuckoo_abstract.json"
echo ""





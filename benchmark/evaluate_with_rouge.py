#!/usr/bin/env python
"""使用ROUGE指标评估摘要质量"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False
    print("Warning: rouge_score not available. Install with: pip install rouge-score")


def evaluate_with_rouge(results_file: str) -> dict:
    """使用ROUGE指标评估结果"""
    if not ROUGE_AVAILABLE:
        print("Error: rouge_score library not installed")
        print("Install with: pip install rouge-score")
        return {}
    
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    rouge1_scores = []
    rouge2_scores = []
    rougeL_scores = []
    
    detailed_results = []
    
    for result in results:
        prediction = result.get("answer", "")
        reference = result.get("expected_answer", "")
        
        if not prediction or not reference:
            continue
        
        scores = scorer.score(reference, prediction)
        
        rouge1_scores.append(scores['rouge1'].fmeasure)
        rouge2_scores.append(scores['rouge2'].fmeasure)
        rougeL_scores.append(scores['rougeL'].fmeasure)
        
        detailed_results.append({
            "question": result.get("question", "")[:50],
            "rouge1": scores['rouge1'].fmeasure,
            "rouge2": scores['rouge2'].fmeasure,
            "rougeL": scores['rougeL'].fmeasure,
        })
    
    avg_scores = {
        "rouge1": sum(rouge1_scores) / len(rouge1_scores) if rouge1_scores else 0.0,
        "rouge2": sum(rouge2_scores) / len(rouge2_scores) if rouge2_scores else 0.0,
        "rougeL": sum(rougeL_scores) / len(rougeL_scores) if rougeL_scores else 0.0,
    }
    
    return {
        "average_scores": avg_scores,
        "total_samples": len(results),
        "detailed_results": detailed_results[:10],
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="使用ROUGE指标评估摘要质量")
    parser.add_argument('--results', type=str, required=True,
                       help='测试结果JSON文件路径')
    parser.add_argument('--output', type=str, default=None,
                       help='输出评估结果文件路径')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("使用ROUGE指标评估摘要质量")
    print("=" * 80)
    
    evaluation = evaluate_with_rouge(args.results)
    
    if not evaluation:
        return
    
    print(f"\n总样本数: {evaluation['total_samples']}")
    print(f"\n平均ROUGE分数:")
    for key, value in evaluation['average_scores'].items():
        print(f"  {key.upper()}: {value:.4f}")
    
    print(f"\n前10个详细结果:")
    for i, result in enumerate(evaluation['detailed_results'], 1):
        print(f"\n[{i}] {result['question']}...")
        print(f"    ROUGE-1: {result['rouge1']:.4f}")
        print(f"    ROUGE-2: {result['rouge2']:.4f}")
        print(f"    ROUGE-L: {result['rougeL']:.4f}")
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(evaluation, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 评估结果已保存到: {args.output}")
    
    print("\n" + "=" * 80)
    print("注意：ROUGE指标专门用于摘要任务评估")
    print("ROUGE-L是最常用的摘要质量指标")
    print("=" * 80)


if __name__ == "__main__":
    main()


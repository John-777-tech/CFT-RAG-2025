#!/usr/bin/env python
"""评估准确度 - 使用更接近论文的方法"""

import json
import sys
from pathlib import Path
from typing import List, Dict
import re

sys.path.insert(0, str(Path(__file__).parent.parent))


def calculate_rouge_l_score(prediction: str, reference: str) -> float:
    """计算ROUGE-L分数（简化版）"""
    if not prediction or not reference:
        return 0.0
    
    pred_words = set(prediction.lower().split())
    ref_words = set(reference.lower().split())
    
    if not ref_words:
        return 0.0
    
    # 计算交集
    intersection = pred_words & ref_words
    if not intersection:
        return 0.0
    
    # 简化的ROUGE-L：基于最长公共子序列的思想
    precision = len(intersection) / len(pred_words) if pred_words else 0
    recall = len(intersection) / len(ref_words) if ref_words else 0
    
    if precision + recall == 0:
        return 0.0
    
    f1 = 2 * precision * recall / (precision + recall)
    return f1


def calculate_semantic_similarity(prediction: str, reference: str) -> float:
    """计算语义相似度（基于关键词匹配）"""
    if not prediction or not reference:
        return 0.0
    
    pred_lower = prediction.lower()
    ref_lower = reference.lower()
    
    # 提取关键词（长度>=4的单词）
    pred_keywords = set([w for w in pred_lower.split() if len(w) >= 4])
    ref_keywords = set([w for w in ref_lower.split() if len(w) >= 4])
    
    if not ref_keywords:
        return 0.0
    
    # 计算关键词重叠率
    overlap = len(pred_keywords & ref_keywords)
    recall = overlap / len(ref_keywords) if ref_keywords else 0
    
    return recall


def evaluate_answer(prediction: str, reference: str) -> Dict[str, float]:
    """评估单个回答"""
    scores = {
        "rouge_l": calculate_rouge_l_score(prediction, reference),
        "semantic_similarity": calculate_semantic_similarity(prediction, reference),
    }
    
    # 综合评分（加权平均）
    scores["overall"] = 0.6 * scores["rouge_l"] + 0.4 * scores["semantic_similarity"]
    
    return scores


def evaluate_results(results_file: str) -> Dict:
    """评估测试结果文件"""
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    all_scores = {
        "rouge_l": [],
        "semantic_similarity": [],
        "overall": [],
    }
    
    detailed_results = []
    
    for result in results:
        prediction = result.get("answer", "")
        reference = result.get("expected_answer", "")
        
        scores = evaluate_answer(prediction, reference)
        
        for key in all_scores:
            all_scores[key].append(scores[key])
        
        detailed_results.append({
            "question": result.get("question", "")[:50],
            "prediction": prediction[:100],
            "reference": reference[:100],
            **scores
        })
    
    # 计算平均分
    avg_scores = {
        key: sum(values) / len(values) if values else 0.0
        for key, values in all_scores.items()
    }
    
    # 计算准确率（overall > 0.3视为正确）
    accuracy = sum(1 for score in all_scores["overall"] if score > 0.3) / len(all_scores["overall"]) if all_scores["overall"] else 0.0
    
    return {
        "average_scores": avg_scores,
        "accuracy": accuracy,
        "total_samples": len(results),
        "detailed_results": detailed_results[:10]  # 只显示前10个
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="评估benchmark结果准确度")
    parser.add_argument('--results', type=str, required=True,
                       help='测试结果JSON文件路径')
    parser.add_argument('--output', type=str, default=None,
                       help='输出评估结果文件路径')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("评估Benchmark结果准确度")
    print("=" * 80)
    
    evaluation = evaluate_results(args.results)
    
    print(f"\n总样本数: {evaluation['total_samples']}")
    print(f"\n平均分数:")
    for key, value in evaluation['average_scores'].items():
        print(f"  {key}: {value:.4f}")
    
    print(f"\n准确率 (overall > 0.3): {evaluation['accuracy']:.2%}")
    
    print(f"\n前10个详细结果:")
    for i, result in enumerate(evaluation['detailed_results'], 1):
        print(f"\n[{i}] {result['question']}...")
        print(f"    ROUGE-L: {result['rouge_l']:.4f}")
        print(f"    语义相似度: {result['semantic_similarity']:.4f}")
        print(f"    综合评分: {result['overall']:.4f}")
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(evaluation, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 评估结果已保存到: {args.output}")
    
    print("\n" + "=" * 80)
    print("注意：这是简化版的评估方法")
    print("论文中使用LangSmith进行更准确的评估")
    print("=" * 80)


if __name__ == "__main__":
    main()



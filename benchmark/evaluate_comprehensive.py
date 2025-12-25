#!/usr/bin/env python
"""使用多种指标评估摘要质量：ROUGE, BLEU, BERTScore"""

import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# 设置HuggingFace镜像（如果环境变量未设置）
if 'HF_ENDPOINT' not in os.environ:
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# ROUGE
try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False
    print("Warning: rouge_score not available. Install with: pip install rouge-score")

# BLEU
try:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from nltk.tokenize import word_tokenize
    BLEU_AVAILABLE = True
    try:
        # 尝试下载punkt tokenizer（如果还没有）
        import nltk
        try:
            nltk.download('punkt_tab', quiet=True)
        except:
            try:
                nltk.download('punkt', quiet=True)
            except:
                pass
    except:
        pass
except ImportError:
    BLEU_AVAILABLE = False
    print("Warning: nltk not available. Install with: pip install nltk")

# BERTScore
try:
    import bert_score
    BERTSCORE_AVAILABLE = True
except ImportError:
    BERTSCORE_AVAILABLE = False
    print("Warning: bert_score not available. Install with: pip install bert-score")


def evaluate_with_rouge(prediction: str, reference: str, scorer):
    """使用ROUGE指标评估"""
    if not ROUGE_AVAILABLE:
        return None
    
    scores = scorer.score(reference, prediction)
    return {
        'rouge1': scores['rouge1'].fmeasure,
        'rouge2': scores['rouge2'].fmeasure,
        'rougeL': scores['rougeL'].fmeasure,
    }


def evaluate_with_bleu(prediction: str, reference: str):
    """使用BLEU指标评估"""
    if not BLEU_AVAILABLE:
        return None
    
    try:
        # Tokenize
        pred_tokens = word_tokenize(prediction.lower())
        ref_tokens = word_tokenize(reference.lower())
        
        # 计算BLEU分数（使用smoothing function处理零匹配情况）
        smoothing_function = SmoothingFunction().method1
        bleu_score = sentence_bleu(
            [ref_tokens], 
            pred_tokens,
            smoothing_function=smoothing_function
        )
        
        return float(bleu_score)
    except Exception as e:
        print(f"BLEU计算错误: {e}")
        return None


def evaluate_with_bertscore(predictions: list, references: list, batch_size: int = 32, model_path: str = None):
    """使用BERTScore评估（批量处理）
    
    Args:
        predictions: 预测文本列表
        references: 参考文本列表
        batch_size: 批处理大小
        model_path: 本地模型路径（可选，如果提供则使用本地模型）
    """
    if not BERTSCORE_AVAILABLE:
        return None
    
    try:
        print("  正在计算BERTScore...")
        if model_path:
            print(f"  使用本地模型: {model_path}")
        
        # BERTScore参数
        score_kwargs = {
            'lang': 'en',
            'verbose': True,  # 显示进度
            'batch_size': batch_size,
            'device': 'cpu'  # 明确指定使用CPU
        }
        
        # 如果提供了本地模型路径，使用model_type参数指向本地路径
        # 注意：BERTScore的model_type参数可以接受本地路径
        if model_path and os.path.exists(model_path):
            score_kwargs['model_type'] = model_path
        
        P, R, F1 = bert_score.score(
            predictions, 
            references, 
            **score_kwargs
        )
        
        # 返回F1分数列表
        return F1.tolist()
    except Exception as e:
        print(f"BERTScore计算错误: {e}")
        print("\n提示：如果网络连接有问题，可以：")
        print("1. 设置环境变量 HF_ENDPOINT=https://hf-mirror.com")
        print("2. 或者先下载模型到本地，然后使用本地路径")
        import traceback
        traceback.print_exc()
        return None


def evaluate_comprehensive(results_file: str, skip_bertscore: bool = False) -> dict:
    """使用多种指标评估结果"""
    
    # 读取结果
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # 初始化ROUGE scorer
    rouge_scorer_obj = None
    if ROUGE_AVAILABLE:
        rouge_scorer_obj = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    # 收集所有predictions和references用于BERTScore批量计算
    predictions = []
    references = []
    valid_indices = []
    
    for i, result in enumerate(results):
        prediction = result.get("answer", "")
        reference = result.get("expected_answer", "")
        
        if not prediction or not reference:
            continue
        
        predictions.append(prediction)
        references.append(reference)
        valid_indices.append(i)
    
    # ROUGE评估
    rouge1_scores = []
    rouge2_scores = []
    rougeL_scores = []
    
    # BLEU评估
    bleu_scores = []
    
    # 逐个样本评估ROUGE和BLEU
    for pred, ref in zip(predictions, references):
        # ROUGE
        if rouge_scorer_obj:
            rouge_scores = evaluate_with_rouge(pred, ref, rouge_scorer_obj)
            if rouge_scores:
                rouge1_scores.append(rouge_scores['rouge1'])
                rouge2_scores.append(rouge_scores['rouge2'])
                rougeL_scores.append(rouge_scores['rougeL'])
        
        # BLEU
        bleu_score = evaluate_with_bleu(pred, ref)
        if bleu_score is not None:
            bleu_scores.append(bleu_score)
    
    # BERTScore批量评估
    bertscore_scores = None
    if BERTSCORE_AVAILABLE and len(predictions) > 0 and not skip_bertscore:
        print(f"\n正在计算BERTScore（{len(predictions)}个样本）...")
        print("  注意：首次运行需要下载BERT模型（roberta-large，约1.3GB）")
        print("  如果网络连接有问题，可以：")
        print("  1. 设置环境变量: export HF_ENDPOINT=https://hf-mirror.com")
        print("  2. 或使用 --skip-bertscore 跳过BERTScore评估")
        print("  3. 下载可能需要10-20分钟，请耐心等待...")
        
        # 尝试使用ModelScope或镜像
        import os
        hf_endpoint = os.environ.get('HF_ENDPOINT', '')
        if hf_endpoint:
            print(f"  使用HuggingFace镜像: {hf_endpoint}")
        
        bertscore_scores = evaluate_with_bertscore(
            predictions, 
            references, 
            batch_size=min(32, len(predictions))
        )
    elif skip_bertscore:
        print("\n跳过BERTScore评估（使用 --skip-bertscore 参数）")
    
    # 计算平均值
    avg_scores = {}
    
    if rouge1_scores:
        avg_scores['rouge1'] = sum(rouge1_scores) / len(rouge1_scores)
        avg_scores['rouge2'] = sum(rouge2_scores) / len(rouge2_scores)
        avg_scores['rougeL'] = sum(rougeL_scores) / len(rougeL_scores)
    
    if bleu_scores:
        avg_scores['bleu'] = sum(bleu_scores) / len(bleu_scores)
    
    if bertscore_scores:
        avg_scores['bertscore'] = sum(bertscore_scores) / len(bertscore_scores)
    
    # 构建详细结果
    detailed_results = []
    for idx, result_idx in enumerate(valid_indices):
        result = results[result_idx]
        detail = {
            "question": result.get("question", "")[:50],
        }
        
        if idx < len(rouge1_scores):
            detail['rouge1'] = rouge1_scores[idx]
            detail['rouge2'] = rouge2_scores[idx]
            detail['rougeL'] = rougeL_scores[idx]
        
        if idx < len(bleu_scores):
            detail['bleu'] = bleu_scores[idx]
        
        if bertscore_scores and idx < len(bertscore_scores):
            detail['bertscore'] = float(bertscore_scores[idx])
        
        detailed_results.append(detail)
    
    return {
        "average_scores": avg_scores,
        "total_samples": len(valid_indices),
        "detailed_results": detailed_results[:10],  # 只显示前10个
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="使用多种指标评估摘要质量（ROUGE, BLEU, BERTScore）")
    parser.add_argument('--results', type=str, required=True,
                       help='测试结果JSON文件路径')
    parser.add_argument('--output', type=str, default=None,
                       help='输出评估结果文件路径')
    parser.add_argument('--skip-bertscore', action='store_true',
                       help='跳过BERTScore评估（BERTScore首次运行需要下载模型，较慢）')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("使用多种指标评估摘要质量")
    print("=" * 80)
    print("\n支持的指标:")
    print(f"  ROUGE: {'✓' if ROUGE_AVAILABLE else '✗'}")
    print(f"  BLEU: {'✓' if BLEU_AVAILABLE else '✗'}")
    print(f"  BERTScore: {'✓' if BERTSCORE_AVAILABLE else '✗'}")
    print("=" * 80)
    
    evaluation = evaluate_comprehensive(args.results, skip_bertscore=args.skip_bertscore)
    
    if not evaluation:
        return
    
    print(f"\n总样本数: {evaluation['total_samples']}")
    print(f"\n平均分数:")
    for key, value in evaluation['average_scores'].items():
        print(f"  {key.upper()}: {value:.4f}")
    
    print(f"\n前10个详细结果:")
    for i, result in enumerate(evaluation['detailed_results'], 1):
        print(f"\n[{i}] {result.get('question', '')}...")
        if 'rouge1' in result:
            print(f"    ROUGE-1: {result['rouge1']:.4f}")
            print(f"    ROUGE-2: {result['rouge2']:.4f}")
            print(f"    ROUGE-L: {result['rougeL']:.4f}")
        if 'bleu' in result:
            print(f"    BLEU: {result['bleu']:.4f}")
        if 'bertscore' in result:
            print(f"    BERTScore: {result['bertscore']:.4f}")
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(evaluation, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 评估结果已保存到: {args.output}")
    
    print("\n" + "=" * 80)
    print("指标说明：")
    print("  ROUGE: 基于n-gram重叠的摘要评估指标")
    print("  BLEU: 基于n-gram精确匹配的翻译/摘要评估指标")
    print("  BERTScore: 基于BERT语义相似度的评估指标")
    print("=" * 80)


if __name__ == "__main__":
    main()


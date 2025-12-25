#!/usr/bin/env python
"""运行baseline RAG的benchmark并计算评估指标
使用search_method=0（标准向量数据库RAG）作为baseline
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_benchmark(dataset_name: str, dataset_path: str, vec_db_key: str, 
                  entities_file_name: str = "entities_file",
                  max_samples: int = None, output_dir: str = "./benchmark/results"):
    """运行benchmark测试"""
    print("=" * 80)
    print(f"运行Baseline RAG Benchmark ({dataset_name})")
    print("=" * 80)
    
    # 构建输出路径
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{dataset_name}_baseline_results.json")
    checkpoint_file = output_file  # 使用相同文件作为checkpoint
    
    # 构建命令
    cmd = [
        sys.executable, 
        "benchmark/run_benchmark.py",
        "--dataset", dataset_path,
        "--vec-db-key", vec_db_key,
        "--search-method", "0",  # Baseline: 标准向量数据库RAG
        "--entities-file-name", entities_file_name,
        "--output", output_file,
        "--checkpoint", checkpoint_file,
    ]
    
    if max_samples:
        cmd.extend(["--max-samples", str(max_samples)])
    
    print(f"\n执行命令: {' '.join(cmd)}\n")
    
    # 运行benchmark
    try:
        result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent.parent)
        print(f"\n✓ Benchmark完成，结果保存在: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Benchmark运行失败: {e}")
        return None


def run_evaluation(results_file: str, output_dir: str = "./benchmark/results", 
                   skip_bertscore: bool = False):
    """运行评估指标计算"""
    print("\n" + "=" * 80)
    print("计算评估指标 (ROUGE, BLEU, BERTScore)")
    print("=" * 80)
    
    # 构建输出路径
    os.makedirs(output_dir, exist_ok=True)
    dataset_name = Path(results_file).stem.replace("_baseline_results", "")
    eval_output = os.path.join(output_dir, f"{dataset_name}_baseline_evaluation.json")
    
    # 构建命令
    cmd = [
        sys.executable,
        "benchmark/evaluate_comprehensive.py",
        "--results", results_file,
        "--output", eval_output,
    ]
    
    if skip_bertscore:
        cmd.append("--skip-bertscore")
    
    print(f"\n执行命令: {' '.join(cmd)}\n")
    
    # 运行评估
    try:
        result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent.parent)
        print(f"\n✓ 评估完成，结果保存在: {eval_output}")
        return eval_output
    except subprocess.CalledProcessError as e:
        print(f"\n✗ 评估运行失败: {e}")
        return None


def print_summary(eval_file: str):
    """打印评估结果摘要"""
    if not os.path.exists(eval_file):
        print(f"评估结果文件不存在: {eval_file}")
        return
    
    with open(eval_file, 'r', encoding='utf-8') as f:
        eval_data = json.load(f)
    
    print("\n" + "=" * 80)
    print("Baseline RAG 评估结果摘要")
    print("=" * 80)
    print(f"\n总样本数: {eval_data.get('total_samples', 0)}")
    print("\n平均分数:")
    avg_scores = eval_data.get('average_scores', {})
    for metric, score in avg_scores.items():
        print(f"  {metric.upper()}: {score:.4f}")
    
    print("\n" + "=" * 80)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="运行baseline RAG的benchmark并计算评估指标"
    )
    parser.add_argument('--dataset', type=str, required=True,
                       help='数据集名称 (例如: aeslc, medqa, dart)')
    parser.add_argument('--dataset-path', type=str, required=True,
                       help='数据集JSON文件路径')
    parser.add_argument('--vec-db-key', type=str, default="test",
                       help='向量数据库key')
    parser.add_argument('--entities-file-name', type=str, default="entities_file",
                       help='实体文件名（不含.csv扩展名）')
    parser.add_argument('--max-samples', type=int, default=None,
                       help='最大测试样本数（用于快速测试）')
    parser.add_argument('--skip-bertscore', action='store_true',
                       help='跳过BERTScore评估（首次运行需要下载模型，较慢）')
    parser.add_argument('--output-dir', type=str, default="./benchmark/results",
                       help='输出目录')
    parser.add_argument('--skip-benchmark', action='store_true',
                       help='跳过benchmark运行，只运行评估（如果结果文件已存在）')
    
    args = parser.parse_args()
    
    # 运行benchmark
    results_file = None
    if not args.skip_benchmark:
        results_file = run_benchmark(
            args.dataset,
            args.dataset_path,
            args.vec_db_key,
            args.entities_file_name,
            args.max_samples,
            args.output_dir
        )
    else:
        # 尝试找到现有的结果文件
        results_file = os.path.join(
            args.output_dir, 
            f"{args.dataset}_baseline_results.json"
        )
        if not os.path.exists(results_file):
            print(f"错误: 结果文件不存在: {results_file}")
            print("请先运行benchmark（不使用--skip-benchmark）")
            return
    
    if not results_file or not os.path.exists(results_file):
        print("\n✗ Benchmark未完成，无法进行评估")
        return
    
    # 运行评估
    eval_file = run_evaluation(
        results_file,
        args.output_dir,
        args.skip_bertscore
    )
    
    if eval_file:
        print_summary(eval_file)
        print(f"\n✓ 完整流程完成！")
        print(f"  - Benchmark结果: {results_file}")
        print(f"  - 评估结果: {eval_file}")


if __name__ == "__main__":
    main()



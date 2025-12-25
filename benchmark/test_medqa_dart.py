#!/usr/bin/env python
"""测试MedQA和DART数据集
比较Baseline RAG (search_method=0) vs Tree-RAG (search_method=2)
"""

import sys
import os
import json
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def build_knowledge_base(dataset_name: str, knowledge_dir: str, vec_db_key: str):
    """构建知识库（向量数据库）"""
    print(f"\n{'='*80}")
    print(f"构建 {dataset_name} 知识库")
    print(f"{'='*80}")
    
    # 使用Python脚本构建
    script = f"""
import sys
sys.path.insert(0, '{Path(__file__).parent.parent}')
from rag_base.build_index import load_vec_db

print("正在构建向量数据库...")
db = load_vec_db('{vec_db_key}', '{knowledge_dir}')
print(f"✓ 向量数据库构建完成: {vec_db_key}")
"""
    
    result = subprocess.run(
        ['python3', '-c', script],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent)
    )
    
    if result.returncode != 0:
        print(f"✗ 构建失败: {result.stderr}")
        return False
    
    print(result.stdout)
    return True


def run_benchmark(dataset_name: str, dataset_file: str, vec_db_key: str, 
                  entities_file: str, search_method: int, output_file: str, 
                  max_samples: int = 100):
    """运行benchmark测试"""
    print(f"\n{'='*80}")
    print(f"运行 {dataset_name} Benchmark (search_method={search_method})")
    print(f"{'='*80}")
    
    cmd = [
        'python3', 'benchmark/run_benchmark.py',
        '--dataset', dataset_file,
        '--vec-db-key', vec_db_key,
        '--entities-file-name', entities_file,
        '--tree-num-max', '50',
        '--search-method', str(search_method),
        '--output', output_file,
        '--max-samples', str(max_samples)
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent)
    )
    
    if result.returncode != 0:
        print(f"✗ Benchmark运行失败: {result.stderr}")
        return False
    
    print(result.stdout)
    return True


def evaluate_results(results_file: str):
    """评估结果"""
    print(f"\n{'='*80}")
    print(f"评估结果: {results_file}")
    print(f"{'='*80}")
    
    cmd = [
        'python3', 'benchmark/evaluate_comprehensive.py',
        '--results', results_file,
        '--skip-bertscore'  # 跳过BERTScore以加快速度
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent)
    )
    
    if result.returncode != 0:
        print(f"✗ 评估失败: {result.stderr}")
        return None
    
    print(result.stdout)
    
    # 读取评估结果
    eval_file = results_file.replace('.json', '_evaluation.json')
    if os.path.exists(eval_file):
        with open(eval_file, 'r') as f:
            return json.load(f)
    return None


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="测试MedQA和DART数据集")
    parser.add_argument('--dataset', type=str, choices=['medqa', 'dart', 'both'],
                       default='medqa', help='要测试的数据集')
    parser.add_argument('--max-samples', type=int, default=100,
                       help='每个数据集的最大样本数（用于快速测试）')
    parser.add_argument('--skip-build', action='store_true',
                       help='跳过知识库构建（使用已有的）')
    
    args = parser.parse_args()
    
    # MedQA配置
    medqa_config = {
        'knowledge_dir': '/Users/zongyikun/Downloads/Med_data_clean/textbooks/en',
        'vec_db_key': 'medqa',
        'entities_file': 'medqa_entities_file',
        'dataset_file': './datasets/processed/medqa.json'
    }
    
    # DART配置（暂时使用MedQA的知识库，后续可以替换）
    dart_config = {
        'knowledge_dir': '/Users/zongyikun/Downloads/Med_data_clean/textbooks/en',  # 临时
        'vec_db_key': 'dart',
        'entities_file': 'dart_entities_file',
        'dataset_file': './datasets/processed/dart.json'
    }
    
    results = {}
    
    # 测试MedQA
    if args.dataset in ['medqa', 'both']:
        if not args.skip_build:
            build_knowledge_base('MedQA', medqa_config['knowledge_dir'], 
                                medqa_config['vec_db_key'])
        
        # Baseline (search_method=0)
        baseline_file = './benchmark/results/medqa_baseline.json'
        run_benchmark('MedQA Baseline', medqa_config['dataset_file'],
                     medqa_config['vec_db_key'], medqa_config['entities_file'],
                     0, baseline_file, args.max_samples)
        results['medqa_baseline'] = evaluate_results(baseline_file)
        
        # Tree-RAG (search_method=2)
        treerag_file = './benchmark/results/medqa_treerag.json'
        run_benchmark('MedQA Tree-RAG', medqa_config['dataset_file'],
                     medqa_config['vec_db_key'], medqa_config['entities_file'],
                     2, treerag_file, args.max_samples)
        results['medqa_treerag'] = evaluate_results(treerag_file)
    
    # 测试DART
    if args.dataset in ['dart', 'both']:
        if not args.skip_build:
            build_knowledge_base('DART', dart_config['knowledge_dir'],
                                dart_config['vec_db_key'])
        
        # Baseline (search_method=0)
        baseline_file = './benchmark/results/dart_baseline.json'
        run_benchmark('DART Baseline', dart_config['dataset_file'],
                     dart_config['vec_db_key'], dart_config['entities_file'],
                     0, baseline_file, args.max_samples)
        results['dart_baseline'] = evaluate_results(baseline_file)
        
        # Tree-RAG (search_method=2)
        treerag_file = './benchmark/results/dart_treerag.json'
        run_benchmark('DART Tree-RAG', dart_config['dataset_file'],
                     dart_config['vec_db_key'], dart_config['entities_file'],
                     2, treerag_file, args.max_samples)
        results['dart_treerag'] = evaluate_results(treerag_file)
    
    # 打印对比结果
    print(f"\n{'='*80}")
    print("对比结果总结")
    print(f"{'='*80}")
    
    for dataset_type in ['medqa', 'dart']:
        if f'{dataset_type}_baseline' in results and f'{dataset_type}_treerag' in results:
            baseline = results[f'{dataset_type}_baseline']
            treerag = results[f'{dataset_type}_treerag']
            
            if baseline and treerag:
                print(f"\n{dataset_type.upper()}:")
                print(f"  Baseline ROUGE-L: {baseline['average_scores'].get('rougeL', 0):.4f}")
                print(f"  Tree-RAG ROUGE-L: {treerag['average_scores'].get('rougeL', 0):.4f}")
                improvement = (treerag['average_scores'].get('rougeL', 0) - 
                              baseline['average_scores'].get('rougeL', 0))
                print(f"  提升: {improvement:+.4f} ({improvement*100/baseline['average_scores'].get('rougeL', 0.001):.2f}%)")


if __name__ == "__main__":
    main()



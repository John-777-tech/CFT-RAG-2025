#!/usr/bin/env python
"""数据集加载和转换脚本
支持MedQA, AESLC, DART数据集
支持从ModelScope或HuggingFace加载（使用镜像）
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 设置HuggingFace镜像（默认使用镜像，速度更快）
if 'HF_ENDPOINT' not in os.environ:
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 尝试导入ModelScope（可选）
MODELSCOPE_AVAILABLE = False
try:
    from modelscope.msdatasets import MsDataset
    MODELSCOPE_AVAILABLE = True
except ImportError:
    pass

# 尝试导入HuggingFace datasets（必需）
HUGGINGFACE_AVAILABLE = False
try:
    from datasets import load_dataset
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    print("请安装 datasets 库: pip install datasets")
    sys.exit(1)


def load_medqa_dataset(data_dir: str = None, use_modelscope: bool = False, 
                      from_huggingface: bool = True) -> List[Dict[str, str]]:
    """加载MedQA数据集
    MedQA格式: JSONL文件，每行包含question和answer
    
    Args:
        data_dir: 本地数据集目录（如果已有本地文件）
        use_modelscope: 是否尝试使用ModelScope
        from_huggingface: 是否尝试从HuggingFace下载（bigbio/med_qa）
    """
    results = []
    
    # 尝试从HuggingFace加载（推荐）
    if from_huggingface and HUGGINGFACE_AVAILABLE:
        try:
            print("尝试从HuggingFace加载MedQA数据集...")
            print("  使用镜像: {}".format(os.environ.get('HF_ENDPOINT', 'default')))
            # MedQA在HuggingFace上的ID可能是 bigbio/med_qa
            dataset = load_dataset("bigbio/med_qa", name="med_qa_en", split="test")
            
            for item in dataset:
                # 根据bigbio/med_qa的格式提取数据
                # 格式可能不同，需要根据实际情况调整
                question = item.get('question', item.get('input', ''))
                answer = item.get('answer', item.get('target', item.get('final_answer', '')))
                
                if question and answer:
                    results.append({
                        "prompt": question,
                        "answer": str(answer) if answer else ""
                    })
            
            if results:
                print(f"✓ 从HuggingFace成功加载 {len(results)} 条MedQA数据")
                return results
        except Exception as e:
            print(f"⚠ 从HuggingFace加载MedQA失败: {e}")
            print("  尝试使用本地文件...")
    
    # 从本地文件加载（如果HuggingFace失败）
    dataset_path = data_dir or "./datasets/MedQA"
    
    if not os.path.exists(dataset_path):
        print(f"MedQA数据集路径不存在: {dataset_path}")
        print("\n请选择以下方式之一下载MedQA数据集：")
        print("1. 从HuggingFace下载（如果可用）")
        print("2. 从GitHub下载: https://github.com/jind11/MedQA")
        print("3. 访问 https://huggingface.co/datasets/bigbio/med_qa")
        return []
    
    results = []
    
    # 尝试查找JSONL文件
    jsonl_files = list(Path(dataset_path).glob("*.jsonl")) + \
                  list(Path(dataset_path).rglob("*.jsonl"))
    
    if not jsonl_files:
        print(f"在 {dataset_path} 中未找到JSONL文件")
        return []
    
    for jsonl_file in jsonl_files[:1]:  # 只处理第一个文件
        print(f"加载MedQA文件: {jsonl_file}")
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    # MedQA格式可能包含多个字段，提取question和answer
                    question = data.get('question', data.get('Question', ''))
                    answer = data.get('answer', data.get('Answer', data.get('final_answer', '')))
                    
                    if question and answer:
                        results.append({
                            "prompt": question,
                            "answer": str(answer)
                        })
                except json.JSONDecodeError as e:
                    print(f"跳过无效JSON行 {line_num}: {e}")
                    continue
                
                # 限制数量用于测试
                if len(results) >= 100:
                    break
        
        if results:
            break
    
    print(f"成功加载 {len(results)} 条MedQA数据")
    return results


def load_aeslc_dataset(split: str = "test", use_modelscope: bool = False) -> List[Dict[str, str]]:
    """加载AESLC数据集
    支持从ModelScope或HuggingFace加载
    AESLC包含邮件主题行和正文，我们将主题行作为问题，正文作为答案
    """
    results = []
    
    # 尝试从ModelScope加载（如果可用且用户指定）
    if use_modelscope and MODELSCOPE_AVAILABLE:
        try:
            print(f"尝试从ModelScope加载AESLC数据集 ({split} split)...")
            dataset = MsDataset.load("Yale-LILY/aeslc", subset_name="default", split=split)
            
            for item in dataset:
                data = dict(item) if not isinstance(item, dict) else item
                subject = data.get('subject_line', '')
                body = data.get('email_body', '')
                
                if subject and body:
                    results.append({
                        "prompt": f"Summarize the following email: {subject}",
                        "answer": body[:500]
                    })
            
            if results:
                print(f"✓ 从ModelScope成功加载 {len(results)} 条AESLC数据")
                return results
        except Exception as e:
            print(f"⚠ ModelScope加载失败: {e}")
            print("  回退到HuggingFace...")
    
    # 从HuggingFace加载（使用镜像，默认方式）
    if HUGGINGFACE_AVAILABLE:
        try:
            print(f"从HuggingFace加载AESLC数据集 ({split} split)...")
            print(f"  使用镜像: {os.environ.get('HF_ENDPOINT', 'default')}")
            dataset = load_dataset("Yale-LILY/aeslc", split=split)
            
            for item in dataset:
                subject = item.get('subject_line', '')
                body = item.get('email_body', '')
                
                if subject and body:
                    results.append({
                        "prompt": f"Summarize the following email: {subject}",
                        "answer": body[:500]
                    })
            
            print(f"✓ 从HuggingFace成功加载 {len(results)} 条AESLC数据")
            return results
        except Exception as e:
            print(f"✗ 加载AESLC数据集失败: {e}")
            print("提示: 请检查网络连接，或设置 HF_ENDPOINT=https://hf-mirror.com")
    
    return []


def load_dart_dataset(split: str = "test", use_modelscope: bool = False) -> List[Dict[str, str]]:
    """加载DART数据集
    支持从ModelScope或HuggingFace加载
    DART包含三元组和对应的文本描述
    """
    results = []
    
    # 尝试从ModelScope加载（如果可用且用户指定）
    if use_modelscope and MODELSCOPE_AVAILABLE:
        try:
            print(f"尝试从ModelScope加载DART数据集 ({split} split)...")
            dataset = MsDataset.load("dart", subset_name="default", split=split)
            
            for item in dataset:
                data = dict(item) if not isinstance(item, dict) else item
                triples = data.get('tripleset', [])
                target = data.get('target_text', '')
                
                if triples and target:
                    triple_str = " | ".join([f"({t})" for t in triples[:3]])
                    prompt = f"根据以下三元组生成描述: {triple_str}"
                    
                    results.append({
                        "prompt": prompt,
                        "answer": target
                    })
            
            if results:
                print(f"✓ 从ModelScope成功加载 {len(results)} 条DART数据")
                return results
        except Exception as e:
            print(f"⚠ ModelScope加载失败: {e}")
            print("  回退到HuggingFace...")
    
    # 从HuggingFace加载（使用镜像，默认方式）
    if HUGGINGFACE_AVAILABLE:
        try:
            print(f"从HuggingFace加载DART数据集 ({split} split)...")
            print(f"  使用镜像: {os.environ.get('HF_ENDPOINT', 'default')}")
            dataset = load_dataset("dart", split=split)
            
            for item in dataset:
                triples = item.get('tripleset', [])
                target = item.get('target_text', '')
                
                if triples and target:
                    triple_str = " | ".join([f"({t})" for t in triples[:3]])
                    prompt = f"根据以下三元组生成描述: {triple_str}"
                    
                    results.append({
                        "prompt": prompt,
                        "answer": target
                    })
            
            print(f"✓ 从HuggingFace成功加载 {len(results)} 条DART数据")
            return results
        except Exception as e:
            print(f"✗ 加载DART数据集失败: {e}")
            print("提示: 请检查网络连接，或设置 HF_ENDPOINT=https://hf-mirror.com")
    
    return []


def save_dataset_json(dataset: List[Dict[str, str]], output_path: str):
    """保存数据集为JSON格式"""
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"数据集已保存到: {output_path}")


def main():
    """主函数：加载所有数据集"""
    import argparse
    
    parser = argparse.ArgumentParser(description="加载benchmark数据集")
    parser.add_argument('--dataset', type=str, choices=['medqa', 'aeslc', 'dart', 'all'],
                       default='all', help='要加载的数据集')
    parser.add_argument('--medqa-dir', type=str, default='./datasets/MedQA',
                       help='MedQA数据集目录')
    parser.add_argument('--output-dir', type=str, default='./datasets/processed',
                       help='输出目录')
    parser.add_argument('--use-modelscope', action='store_true',
                       help='尝试使用ModelScope加载（如果可用）')
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    all_datasets = {}
    
    if args.dataset in ['medqa', 'all']:
        medqa_data = load_medqa_dataset(args.medqa_dir)
        if medqa_data:
            all_datasets['medqa'] = medqa_data
            save_dataset_json(medqa_data, os.path.join(args.output_dir, 'medqa.json'))
    
    if args.dataset in ['aeslc', 'all']:
        aeslc_data = load_aeslc_dataset('test', use_modelscope=args.use_modelscope)
        if aeslc_data:
            all_datasets['aeslc'] = aeslc_data
            save_dataset_json(aeslc_data, os.path.join(args.output_dir, 'aeslc.json'))
    
    if args.dataset in ['dart', 'all']:
        dart_data = load_dart_dataset('test', use_modelscope=args.use_modelscope)
        if dart_data:
            all_datasets['dart'] = dart_data
            save_dataset_json(dart_data, os.path.join(args.output_dir, 'dart.json'))
    
    # 保存汇总
    if all_datasets:
        save_dataset_json(all_datasets, os.path.join(args.output_dir, 'all_datasets.json'))
        print(f"\n✓ 成功加载 {len(all_datasets)} 个数据集")
        for name, data in all_datasets.items():
            print(f"  - {name}: {len(data)} 条数据")
    else:
        print("\n✗ 未能加载任何数据集")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""为MedQA和DART数据集构建向量数据库和实体树"""

import sys
import json
import os
import csv
from pathlib import Path
from typing import List, Dict, Set, Tuple
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag_base.build_index import load_vec_db
import shutil

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spacy not available, will use simple keyword extraction")


def prepare_chunks_file(chunks: List[str], output_file: str):
    """将chunks保存为文本文件，以便load_vec_db使用"""
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
    
    # 将chunks合并为一个文档，使用标题分隔
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, chunk in enumerate(chunks):
            f.write(f"# Chunk {i}\n")
            f.write(chunk)
            f.write("\n\n")
    
    print(f"✓ Chunks已保存到: {output_file}")


def extract_chunks_from_medqa(dataset_path: str, max_samples: int = None) -> List[str]:
    """从MedQA数据集中提取chunks（答案文本）"""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    chunks = []
    for item in dataset:
        # MedQA包含answer字段
        answer = item.get('answer', item.get('expected_answer', ''))
        if answer and len(answer.strip()) > 0:
            chunks.append(answer.strip())
    
    if max_samples:
        chunks = chunks[:max_samples]
    
    print(f"✓ 从MedQA数据集提取了 {len(chunks)} 个chunks")
    return chunks


def extract_chunks_from_dart(dataset_path: str, max_samples: int = None) -> List[str]:
    """从DART数据集中提取chunks（答案文本）"""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    chunks = []
    for item in dataset:
        # DART包含answer字段
        answer = item.get('answer', item.get('expected_answer', ''))
        if answer and len(answer.strip()) > 0:
            chunks.append(answer.strip())
    
    if max_samples:
        chunks = chunks[:max_samples]
    
    print(f"✓ 从DART数据集提取了 {len(chunks)} 个chunks")
    return chunks


def extract_entities_simple(text: str) -> Set[str]:
    """简单提取实体：使用大写字母开头的单词和常见名词短语"""
    entities = set()
    
    # 提取大写字母开头的单词
    words = re.findall(r'\b[A-Z][a-z]+\b', text)
    entities.update(words[:10])  # 限制数量
    
    # 提取常见的名词短语（2-3个单词的组合）
    noun_phrases = re.findall(r'\b(?:the|a|an)?\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', text)
    entities.update(noun_phrases[:10])
    
    return entities


def build_entities_file_medqa(dataset_path: str, output_path: str, max_samples: int = 500):
    """为MedQA数据集构建实体关系文件"""
    print(f"正在从MedQA数据集提取实体关系...")
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    if max_samples:
        dataset = dataset[:max_samples]
    
    all_entities = set()
    relations = set()
    
    # 使用简单方法提取实体
    print("使用简单方法提取实体...")
    for item in dataset:
        text = item.get('answer', item.get('expected_answer', ''))
        if text:
            entities = extract_entities_simple(text[:500])  # 限制长度
            all_entities.update(entities)
    
    # 创建基于文本的简单关系
    print("创建基于关键词的简单关系...")
    entities_list = list(all_entities)[:100]  # 限制实体数量
    
    # 从数据集中查找共现的实体
    for item in dataset[:200]:  # 只处理前200条以加快速度
        text = item.get('answer', item.get('expected_answer', '')).lower()
        entities_in_text = [e for e in entities_list if e.lower() in text]
        
        # 创建共现实体之间的关系
        for i, e1 in enumerate(entities_in_text[:5]):
            for e2 in entities_in_text[i+1:i+3]:
                if e1 != e2:
                    relations.add((e1, e2))
    
    # 如果还是不够，创建一些层级关系
    if len(relations) < 50:
        # 创建简单的层级关系（基于实体长度或字母顺序）
        entities_sorted = sorted(entities_list, key=len, reverse=True)[:30]
        for i in range(len(entities_sorted) - 1):
            relations.add((entities_sorted[i], entities_sorted[i+1]))
    
    # 保存实体关系文件
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for rel in relations:
            if len(rel) == 2 and rel[0] and rel[1]:
                writer.writerow([rel[0], rel[1]])
    
    print(f"✓ 生成了 {len(relations)} 个实体关系")
    print(f"✓ 实体关系文件已保存到: {output_path}")
    
    return output_path


def build_entities_file_dart(dataset_path: str, output_path: str, max_samples: int = 500):
    """为DART数据集构建实体关系文件"""
    print(f"正在从DART数据集提取实体关系...")
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    if max_samples:
        dataset = dataset[:max_samples]
    
    all_entities = set()
    relations = set()
    
    # 使用简单方法提取实体
    print("使用简单方法提取实体...")
    for item in dataset:
        text = item.get('answer', item.get('expected_answer', ''))
        if text:
            entities = extract_entities_simple(text[:500])  # 限制长度
            all_entities.update(entities)
    
    # 创建基于文本的简单关系
    print("创建基于关键词的简单关系...")
    entities_list = list(all_entities)[:100]  # 限制实体数量
    
    # 从数据集中查找共现的实体
    for item in dataset[:200]:  # 只处理前200条以加快速度
        text = item.get('answer', item.get('expected_answer', '')).lower()
        entities_in_text = [e for e in entities_list if e.lower() in text]
        
        # 创建共现实体之间的关系
        for i, e1 in enumerate(entities_in_text[:5]):
            for e2 in entities_in_text[i+1:i+3]:
                if e1 != e2:
                    relations.add((e1, e2))
    
    # 如果还是不够，创建一些层级关系
    if len(relations) < 50:
        # 创建简单的层级关系（基于实体长度或字母顺序）
        entities_sorted = sorted(entities_list, key=len, reverse=True)[:30]
        for i in range(len(entities_sorted) - 1):
            relations.add((entities_sorted[i], entities_sorted[i+1]))
    
    # 保存实体关系文件
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for rel in relations:
            if len(rel) == 2 and rel[0] and rel[1]:
                writer.writerow([rel[0], rel[1]])
    
    print(f"✓ 生成了 {len(relations)} 个实体关系")
    print(f"✓ 实体关系文件已保存到: {output_path}")
    
    return output_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="为MedQA和DART数据集构建向量数据库和实体树")
    parser.add_argument('--dataset-type', type=str, choices=['medqa', 'dart', 'both'], 
                       default='both', help='要构建的数据集类型')
    parser.add_argument('--medqa-dataset', type=str, default='./datasets/processed/medqa.json',
                       help='MedQA数据集JSON文件路径')
    parser.add_argument('--dart-dataset', type=str, default='./datasets/processed/dart.json',
                       help='DART数据集JSON文件路径')
    parser.add_argument('--medqa-vec-db-key', type=str, default='medqa',
                       help='MedQA向量数据库的key')
    parser.add_argument('--dart-vec-db-key', type=str, default='dart',
                       help='DART向量数据库的key')
    parser.add_argument('--medqa-entities-file', type=str, default='./medqa_entities_file.csv',
                       help='MedQA输出的实体关系文件路径')
    parser.add_argument('--dart-entities-file', type=str, default='./dart_entities_file.csv',
                       help='DART输出的实体关系文件路径')
    parser.add_argument('--medqa-chunks-file', type=str, default='./datasets/medqa_chunks.txt',
                       help='MedQA输出的chunks文本文件路径')
    parser.add_argument('--dart-chunks-file', type=str, default='./datasets/dart_chunks.txt',
                       help='DART输出的chunks文本文件路径')
    parser.add_argument('--max-samples', type=int, default=None,
                       help='最大处理样本数（用于加快构建速度，None表示处理全部）')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("为MedQA和DART数据集构建向量数据库和实体树")
    print("=" * 80)
    
    # 构建MedQA
    if args.dataset_type in ['medqa', 'both']:
        print("\n" + "=" * 80)
        print("构建MedQA数据集")
        print("=" * 80)
        
        # 1. 提取chunks
        if not os.path.exists(args.medqa_dataset):
            print(f"✗ MedQA数据集文件不存在: {args.medqa_dataset}")
        else:
            chunks = extract_chunks_from_medqa(args.medqa_dataset, args.max_samples)
            
            if not chunks:
                print("✗ 未能提取到chunks")
            else:
                # 2. 保存chunks为文本文件
                prepare_chunks_file(chunks, args.medqa_chunks_file)
                
                # 3. 使用load_vec_db构建向量数据库
                print(f"\n正在构建MedQA向量数据库 (key: {args.medqa_vec_db_key})...")
                print("注意：如果数据库已存在，将直接加载")
                
                try:
                    db = load_vec_db(args.medqa_vec_db_key, args.medqa_chunks_file)
                    print(f"✓ MedQA向量数据库构建/加载完成")
                except Exception as e:
                    print(f"✗ 构建MedQA向量数据库失败: {e}")
                    import traceback
                    traceback.print_exc()
                
                # 4. 构建实体关系文件
                build_entities_file_medqa(args.medqa_dataset, args.medqa_entities_file, args.max_samples)
                
                print(f"✓ MedQA构建完成！")
    
    # 构建DART
    if args.dataset_type in ['dart', 'both']:
        print("\n" + "=" * 80)
        print("构建DART数据集")
        print("=" * 80)
        
        # 1. 提取chunks
        if not os.path.exists(args.dart_dataset):
            print(f"✗ DART数据集文件不存在: {args.dart_dataset}")
        else:
            chunks = extract_chunks_from_dart(args.dart_dataset, args.max_samples)
            
            if not chunks:
                print("✗ 未能提取到chunks")
            else:
                # 2. 保存chunks为文本文件
                prepare_chunks_file(chunks, args.dart_chunks_file)
                
                # 3. 使用load_vec_db构建向量数据库
                print(f"\n正在构建DART向量数据库 (key: {args.dart_vec_db_key})...")
                print("注意：如果数据库已存在，将直接加载")
                
                try:
                    db = load_vec_db(args.dart_vec_db_key, args.dart_chunks_file)
                    print(f"✓ DART向量数据库构建/加载完成")
                except Exception as e:
                    print(f"✗ 构建DART向量数据库失败: {e}")
                    import traceback
                    traceback.print_exc()
                
                # 4. 构建实体关系文件
                build_entities_file_dart(args.dart_dataset, args.dart_entities_file, args.max_samples)
                
                print(f"✓ DART构建完成！")
    
    print("\n" + "=" * 80)
    print("✓ 全部构建完成！")
    print("=" * 80)
    print(f"\n下一步：")
    print(f"1. 使用以下命令运行benchmark（Baseline RAG）：")
    print(f"   python benchmark/run_benchmark.py \\")
    print(f"       --dataset ./datasets/processed/medqa.json \\")
    print(f"       --vec-db-key medqa \\")
    print(f"       --entities-file-name medqa_entities_file \\")
    print(f"       --search-method 0 \\")
    print(f"       --max-samples 20")
    print(f"\n2. 使用以下命令运行benchmark（Cuckoo Filter Abstract RAG）：")
    print(f"   python benchmark/run_benchmark.py \\")
    print(f"       --dataset ./datasets/processed/medqa.json \\")
    print(f"       --vec-db-key medqa \\")
    print(f"       --entities-file-name medqa_entities_file \\")
    print(f"       --search-method 7 \\")
    print(f"       --max-samples 20")


if __name__ == "__main__":
    main()





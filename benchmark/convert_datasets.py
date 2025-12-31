#!/usr/bin/env python
"""将用户下载的数据集转换为benchmark格式
- DART: dart-v1.1.1-full-dev.json
- MedQA: Med_data_clean/questions/US/test.jsonl
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def convert_dart_dataset(json_file: str, output_file: str, max_samples: int = None):
    """转换DART数据集
    
    DART格式:
    {
      "tripleset": [["subject", "relation", "object"], ...],
      "annotations": [{"text": "generated text"}]
    }
    
    转换为:
    {
      "prompt": "根据以下三元组生成描述: ...",
      "answer": "generated text"
    }
    """
    import os
    print(f"正在处理DART数据集: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = []
    for item in data:
        triples = item.get('tripleset', [])
        annotations = item.get('annotations', [])
        
        if not triples or not annotations:
            continue
        
        # 使用第一个annotation作为答案
        first_ann = annotations[0]
        target_text = first_ann.get('text', '')
        if not target_text:
            continue
        
        # 获取source字段（如果有）
        source = first_ann.get('source', '')
        
        # 构建prompt
        triple_strs = []
        for triple in triples[:5]:  # 最多5个三元组
            if len(triple) >= 3:
                triple_strs.append(f"({triple[0]}, {triple[1]}, {triple[2]})")
        
        if triple_strs:
            prompt = f"Generate a description based on the following triples: {' | '.join(triple_strs)}"
        else:
            continue
        
        result = {
            "prompt": prompt,
            "answer": target_text,
            "expected_answer": target_text  # DART中answer就是expected_answer
        }
        
        # 保留source字段（用于后续分组）
        if source:
            result["source"] = source
        
        results.append(result)
        
        if max_samples and len(results) >= max_samples:
            break
    
    # 保存
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 转换完成: {len(results)} 条数据 -> {output_file}")
    return results


def convert_medqa_dataset(jsonl_file: str, output_file: str, max_samples: int = None):
    """转换MedQA数据集
    
    MedQA格式 (JSONL):
    {
      "question": "...",
      "answer": "...",
      ...
    }
    
    转换为:
    {
      "prompt": "question",
      "answer": "answer",
      "expected_answer": "answer"
    }
    """
    import os
    print(f"正在处理MedQA数据集: {jsonl_file}")
    
    results = []
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                question = data.get('question', data.get('Question', ''))
                answer = data.get('answer', data.get('Answer', data.get('final_answer', '')))
                
                if question and answer:
                    results.append({
                        "prompt": question,
                        "answer": str(answer),
                        "expected_answer": str(answer)
                    })
            except json.JSONDecodeError as e:
                print(f"跳过无效JSON行 {line_num}: {e}")
                continue
            
            if max_samples and len(results) >= max_samples:
                break
    
    # 保存
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 转换完成: {len(results)} 条数据 -> {output_file}")
    return results


def main():
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="转换用户下载的数据集")
    parser.add_argument('--dart-file', type=str, 
                       default='/Users/zongyikun/Downloads/dart-v1.1.1-full-dev.json',
                       help='DART数据集JSON文件路径')
    parser.add_argument('--medqa-file', type=str,
                       default='/Users/zongyikun/Downloads/Med_data_clean/questions/US/test.jsonl',
                       help='MedQA数据集JSONL文件路径')
    parser.add_argument('--output-dir', type=str, default='./datasets/processed',
                       help='输出目录')
    parser.add_argument('--max-samples', type=int, default=None,
                       help='限制每个数据集的样本数量（用于快速测试）')
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 转换DART
    dart_output = os.path.join(args.output_dir, 'dart.json')
    if os.path.exists(args.dart_file):
        convert_dart_dataset(args.dart_file, dart_output, args.max_samples)
    else:
        print(f"⚠ DART文件不存在: {args.dart_file}")
    
    # 转换MedQA
    medqa_output = os.path.join(args.output_dir, 'medqa.json')
    if os.path.exists(args.medqa_file):
        convert_medqa_dataset(args.medqa_file, medqa_output, args.max_samples)
    else:
        print(f"⚠ MedQA文件不存在: {args.medqa_file}")


if __name__ == "__main__":
    main()


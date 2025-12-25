#!/usr/bin/env python
"""简单测试baseline RAG (search_method=0)"""

import sys
import os
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')

print("=" * 60)
print("测试Baseline RAG (search_method=0)")
print("=" * 60)

# 1. 加载向量数据库
print("\n[1/4] 加载向量数据库...")
from rag_base.build_index import load_vec_db
vec_db = load_vec_db('aeslc', 'vec_db_cache/')
print("✓ 向量数据库加载完成")

# 2. 不加载forest（search_method=0不需要）
print("\n[2/4] search_method=0，跳过forest加载")
forest = None
nlp = None

# 3. 加载测试数据
print("\n[3/4] 加载测试数据...")
with open('./datasets/processed/aeslc.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)
test_data = dataset[:2]  # 只测试2个样本
print(f"✓ 加载了 {len(test_data)} 个测试样本")

# 4. 运行测试
print("\n[4/4] 运行RAG测试 (search_method=0)...")
from rag_base.rag_complete import rag_complete

results = []
for i, item in enumerate(test_data, 1):
    question = item.get("prompt", item.get("question", ""))
    expected = item.get("answer", item.get("expected_answer", ""))
    
    print(f"\n[{i}/{len(test_data)}] 问题: {question[:50]}...")
    start_time = time.time()
    
    try:
        stream = rag_complete(
            question,
            vec_db,
            forest,  # None for search_method=0
            nlp,     # None for search_method=0
            search_method=0,  # Baseline RAG
            debug=False,
        )
        
        answer = ""
        for chunk in stream:
            answer += chunk
        
        elapsed_time = time.time() - start_time
        
        results.append({
            "question": question,
            "answer": answer,
            "expected_answer": expected,
            "time": elapsed_time,
            "answer_length": len(answer)
        })
        
        print(f"  回答长度: {len(answer)} 字符")
        print(f"  耗时: {elapsed_time:.2f}秒")
        
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        import traceback
        traceback.print_exc()

# 5. 保存结果
output_file = './benchmark/results/aeslc_baseline_test_simple.json'
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✓ 测试完成，结果保存到: {output_file}")
print(f"总样本数: {len(results)}")



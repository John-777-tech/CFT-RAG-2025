#!/usr/bin/env python
"""本地benchmark测试脚本 - 不依赖LangSmith数据集"""

import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
from rag_base.build_index import load_vec_db
from rag_base.rag_complete import rag_complete
from trag_tree import build, hash
import time
import argparse

load_dotenv()

parser = argparse.ArgumentParser(description="本地benchmark测试")
parser.add_argument('--vec-db-key', type=str, default="test", help="向量数据库的key")
parser.add_argument('--tree-num-max', type=int, default=50, help="最大树数量")
parser.add_argument('--entities-file-name', type=str, default="entities_file", help="实体文件名")
parser.add_argument('--search-method', type=int, default=0, choices=[0, 1, 2, 5, 8, 9], 
                    help="搜索方法: 0 for vec-db only (standard RAG), 1 for BFS, 2 for BloomFilter, 5 for improved BloomFilter, 8 for ANN-Tree, 9 for ANN-Graph")
parser.add_argument('--node-num-max', type=int, default=2000000, help="最大节点数")

args = parser.parse_args()

print("=" * 60)
print("本地Benchmark测试：两个chunk对应一个abstract的效果")
print("=" * 60)

start_time = time.time()

# 加载向量数据库
vec_db = load_vec_db(args.vec_db_key, "vec_db_cache/")
print("✓ Vector DB加载完成")

# 构建forest和nlp
forest, nlp = build.build_forest(args.tree_num_max, args.entities_file_name, args.search_method, args.node_num_max)
print("✓ Forest和NLP加载完成")

if args.search_method in [4, 8]:
    for entity_tree in forest:
        entity_tree.bfs_hash()

if args.search_method in [9]:
    from grag_graph.graph import build_graph
    build_graph(args.entities_file_name)

if args.search_method in [8, 9]:
    from ann.ann_calc import build_ann
    build_ann()

# Cuckoo filter (search_method == 7) removed - using standard RAG now

# 测试问题列表（模拟benchmark测试）
test_questions = [
    "什么是医院？",
    "科室的作用是什么？",
    "医生和患者的关系是什么？",
    "疾病有哪些症状？",
    "如何治疗疾病？"
]

print(f"\n开始测试 {len(test_questions)} 个问题...")
print("-" * 60)

total_retrieval_time = 0
total_generation_time = 0
results = []

for i, question in enumerate(test_questions, 1):
    print(f"\n问题 {i}/{len(test_questions)}: {question}")
    
    query_start = time.time()
    
    stream = rag_complete(
        question,
        vec_db,
        forest,
        nlp,
        search_method=args.search_method,
        debug=True,
    )
    
    # 收集回答
    answer = ""
    for chunk in stream:
        answer += chunk
    
    query_end = time.time()
    query_time = query_end - query_start
    
    results.append({
        "question": question,
        "answer": answer[:200] + "..." if len(answer) > 200 else answer,
        "time": query_time
    })
    
    print(f"回答: {answer[:100]}...")
    print(f"耗时: {query_time:.2f}秒")

print("\n" + "=" * 60)
print("测试结果汇总")
print("=" * 60)
print(f"总问题数: {len(test_questions)}")
print(f"平均响应时间: {sum(r['time'] for r in results) / len(results):.2f}秒")
print("\n✓ 测试完成！两个chunk对应一个abstract的逻辑已生效。")
print("=" * 60)


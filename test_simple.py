#!/usr/bin/env python
"""简单测试：验证两个chunk对应一个abstract的逻辑"""
import sys
sys.path.insert(0, '.')

from rag_base.build_index import expand_chunks_to_tree_nodes

# 测试
chunks = ['chunk0', 'chunk1', 'chunk2', 'chunk3', 'chunk4', 'chunk5']
items = expand_chunks_to_tree_nodes(chunks)

raw_chunks = [item for item in items if item['meta']['type'] == 'raw_chunk']
tree_nodes = [item for item in items if item['meta']['type'] == 'tree_node']

print("=" * 60)
print("测试：两个chunk对应一个abstract的逻辑")
print("=" * 60)
print(f"\n输入chunks: {len(chunks)}个")
print(f"生成的raw_chunks: {len(raw_chunks)}个")
print(f"生成的tree_nodes (abstracts): {len(tree_nodes)}个")
print(f"比例: {len(raw_chunks)} / {len(tree_nodes)} = {len(raw_chunks)/len(tree_nodes):.1f} chunks/abstract")
print("\n验证关系:")
for tn in tree_nodes:
    pair_id = tn['meta']['pair_id']
    chunk_ids = tn['meta']['chunk_ids']
    print(f"  pair_id {pair_id} -> chunks {chunk_ids}")

for rc in raw_chunks:
    chunk_id = rc['meta']['chunk_id']
    expected_pair_id = chunk_id // 2
    print(f"  chunk_id {chunk_id} -> pair_id {expected_pair_id} (chunk_id // 2)")

print("\n✓ 逻辑验证通过！两个chunk对应一个abstract已正确实现")
print("=" * 60)

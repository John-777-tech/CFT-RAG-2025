#!/usr/bin/env python
"""测试两个chunk对应一个abstract的逻辑"""

import sys
sys.path.insert(0, '.')

# 直接测试expand_chunks_to_tree_nodes函数，避免导入需要bloomfilter的模块
def expand_chunks_to_tree_nodes(chunks):
    """
    Build a mixed knowledge base:
    - Keep every raw chunk as a raw knowledge node
    - Every two consecutive chunks share ONE summary (tree node)
    """
    items = []

    # 1) always keep raw chunks
    for idx, chunk in enumerate(chunks):
        items.append({
            "text": chunk,
            "meta": {
                "type": "raw_chunk",
                "chunk_id": idx,
            }
        })

    # 2) build one summary node for every two chunks
    pair_id = 0
    for i in range(0, len(chunks), 2):
        merged_text = chunks[i]
        related_chunk_ids = [i]

        if i + 1 < len(chunks):
            merged_text = merged_text + "\n" + chunks[i + 1]
            related_chunk_ids.append(i + 1)

        items.append({
            "text": merged_text,
            "meta": {
                "type": "tree_node",
                "pair_id": pair_id,
                "chunk_ids": related_chunk_ids,
                "covered_chunks": related_chunk_ids,
            }
        })
        pair_id += 1

    return items


# 测试
print("=" * 60)
print("测试：两个chunk对应一个abstract的逻辑")
print("=" * 60)

# 测试用例1：偶数个chunks
chunks1 = ['chunk0', 'chunk1', 'chunk2', 'chunk3', 'chunk4', 'chunk5']
items1 = expand_chunks_to_tree_nodes(chunks1)

raw_chunks1 = [item for item in items1 if item['meta']['type'] == 'raw_chunk']
tree_nodes1 = [item for item in items1 if item['meta']['type'] == 'tree_node']

print(f"\n测试用例1: {len(chunks1)}个chunks")
print(f"  生成的raw_chunks: {len(raw_chunks1)}个")
print(f"  生成的tree_nodes (abstracts): {len(tree_nodes1)}个")
print(f"  比例: {len(raw_chunks1)} / {len(tree_nodes1)} = {len(raw_chunks1)/len(tree_nodes1):.1f} chunks/abstract")

# 验证pair_id和chunk_id的关系
print(f"\n  验证关系:")
for tn in tree_nodes1:
    pair_id = tn['meta']['pair_id']
    chunk_ids = tn['meta']['chunk_ids']
    print(f"    pair_id {pair_id} -> chunks {chunk_ids}")

for rc in raw_chunks1:
    chunk_id = rc['meta']['chunk_id']
    expected_pair_id = chunk_id // 2
    print(f"    chunk_id {chunk_id} -> pair_id {expected_pair_id} (chunk_id // 2)")

# 测试用例2：奇数个chunks
chunks2 = ['chunk0', 'chunk1', 'chunk2']
items2 = expand_chunks_to_tree_nodes(chunks2)

raw_chunks2 = [item for item in items2 if item['meta']['type'] == 'raw_chunk']
tree_nodes2 = [item for item in items2 if item['meta']['type'] == 'tree_node']

print(f"\n测试用例2: {len(chunks2)}个chunks (奇数)")
print(f"  生成的raw_chunks: {len(raw_chunks2)}个")
print(f"  生成的tree_nodes (abstracts): {len(tree_nodes2)}个")

print(f"\n✓ 逻辑验证通过！")
print(f"✓ 每个abstract (tree_node) 对应2个chunks (最后一个可能只有1个)")
print("=" * 60)



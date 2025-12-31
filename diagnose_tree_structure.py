#!/usr/bin/env python
"""
诊断AbstractTree结构，分析为什么depth=2表现更差
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from rag_base.build_index import load_vec_db
from trag_tree.build import build_abstract_forest_and_entity_mapping


def analyze_tree_structure(abstract_forest):
    """分析AbstractTree的结构"""
    print("=" * 80)
    print("AbstractTree结构分析")
    print("=" * 80)
    print()
    
    total_trees = len(abstract_forest)
    print(f"Total AbstractTree数量: {total_trees}")
    print()
    
    tree_stats = []
    for i, tree in enumerate(abstract_forest):
        # 获取所有节点
        root = tree.get_root()
        if root is None:
            continue
        
        # 递归收集所有节点
        def collect_all_nodes(node, collected=None):
            if collected is None:
                collected = []
            collected.append(node)
            for child in node.get_children():
                collect_all_nodes(child, collected)
            return collected
        
        nodes = collect_all_nodes(root) if root else []
        
        # 计算树的深度
        def get_max_depth(node, current_depth=0):
            if node is None:
                return current_depth
            children = node.get_children()
            if not children:
                return current_depth + 1
            max_child_depth = max([get_max_depth(child, current_depth + 1) for child in children], default=current_depth + 1)
            return max_child_depth
        
        max_depth = get_max_depth(root) if root else 0
        
        # 统计每层的节点数
        def count_nodes_by_level(node, level=0, level_counts=None):
            if level_counts is None:
                level_counts = {}
            if level not in level_counts:
                level_counts[level] = 0
            level_counts[level] += 1
            
            for child in node.get_children():
                count_nodes_by_level(child, level + 1, level_counts)
            return level_counts
        
        level_counts = count_nodes_by_level(root) if root else {}
        
        tree_stats.append({
            'tree_id': i,
            'node_count': len(nodes),
            'max_depth': max_depth,
            'level_counts': level_counts,
            'has_parent': sum(1 for node in nodes if node.get_parent() is not None),
            'has_children': sum(1 for node in nodes if len(node.get_children()) > 0),
        })
        
        print(f"Tree {i}:")
        print(f"  - 节点数: {len(nodes)}")
        print(f"  - 最大深度: {max_depth}")
        print(f"  - 有父节点的节点数: {tree_stats[-1]['has_parent']}")
        print(f"  - 有子节点的节点数: {tree_stats[-1]['has_children']}")
        print(f"  - 每层节点数: {dict(sorted(level_counts.items()))}")
        print()
    
    # 统计汇总
    print("=" * 80)
    print("统计汇总")
    print("=" * 80)
    print(f"平均节点数: {sum(s['node_count'] for s in tree_stats) / len(tree_stats):.1f}")
    print(f"平均深度: {sum(s['max_depth'] for s in tree_stats) / len(tree_stats):.1f}")
    print(f"最多节点数: {max(s['node_count'] for s in tree_stats)}")
    print(f"最少节点数: {min(s['node_count'] for s in tree_stats)}")
    print(f"最深树: {max(s['max_depth'] for s in tree_stats)}")
    print(f"最浅树: {min(s['max_depth'] for s in tree_stats)}")
    
    # 分析问题
    print()
    print("=" * 80)
    print("问题分析")
    print("=" * 80)
    
    shallow_trees = [s for s in tree_stats if s['max_depth'] <= 2]
    if shallow_trees:
        print(f"⚠️  警告: {len(shallow_trees)} 个Tree的深度 <= 2，层次结构可能不够丰富")
    
    small_trees = [s for s in tree_stats if s['node_count'] < 10]
    if small_trees:
        print(f"⚠️  警告: {len(small_trees)} 个Tree的节点数 < 10，LLM可能无法建立合理的层次关系")
    
    trees_without_parents = [s for s in tree_stats if s['has_parent'] == 0]
    if trees_without_parents:
        print(f"⚠️  警告: {len(trees_without_parents)} 个Tree没有父节点关系（可能是单节点Tree）")


def analyze_parent_expansion(abstract_forest, sample_pair_ids):
    """分析追溯父节点时发生了什么"""
    print()
    print("=" * 80)
    print("追溯父节点分析")
    print("=" * 80)
    print()
    
    print("模拟depth=2追溯过程（使用示例pair_ids）...")
    print()
    
    for pair_id in sample_pair_ids[:5]:  # 只分析前5个
        print(f"Pair ID: {pair_id}")
        
        # 在当前实现中查找node
        found = False
        for tree in abstract_forest:
            node = tree.find_node_by_pair_id(pair_id)
            if node:
                found = True
                print(f"  ✓ 在Tree中找到节点")
                print(f"  节点内容预览: {node.get_content()[:100]}...")
                
                parent = node.get_parent()
                if parent:
                    print(f"  ✓ 有父节点 (pair_id={parent.get_pair_id()})")
                    print(f"  父节点内容预览: {parent.get_content()[:100]}...")
                    
                    # 检查父节点的子节点数
                    children_count = len(parent.get_children())
                    print(f"  父节点有 {children_count} 个子节点")
                    
                    # 检查是否是根节点
                    if parent.get_parent() is None:
                        print(f"  ⚠️  父节点是根节点（可能是顶层概括，内容可能不相关）")
                    else:
                        print(f"  ✓ 父节点不是根节点")
                else:
                    print(f"  ✗ 没有父节点（是根节点）")
                
                break
        
        if not found:
            print(f"  ✗ 未在任何Tree中找到该节点")
        
        print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='诊断AbstractTree结构')
    parser.add_argument('--dataset', type=str, required=True, choices=['medqa', 'dart', 'triviaqa'])
    parser.add_argument('--entities-file', type=str, help='实体列表文件路径')
    
    args = parser.parse_args()
    
    dataset = args.dataset
    if args.entities_file:
        entities_file = args.entities_file
    else:
        entities_file = f"./extracted_data/{dataset}_entities_list.txt"
    
    print("=" * 80)
    print(f"诊断 {dataset} 数据集的AbstractTree结构")
    print("=" * 80)
    print()
    
    # 加载实体列表
    print("加载实体列表...")
    with open(entities_file, 'r', encoding='utf-8') as f:
        entities_list = [line.strip() for line in f if line.strip()]
    print(f"✓ 加载了 {len(entities_list)} 个实体")
    print()
    
    # 加载向量数据库
    print("加载向量数据库...")
    chunks_file = f"./extracted_data/{dataset}_chunks.txt"
    db = load_vec_db(dataset, chunks_file)
    
    # 获取table_name
    from rag_base import build_index
    db_id = id(db)
    table_name = None
    if hasattr(build_index.load_vec_db, '_db_table_map'):
        table_name = build_index.load_vec_db._db_table_map.get(db_id)
    if table_name is None:
        keys = db.get_all_keys()
        table_name = keys[0] if keys else "default_table"
    print(f"✓ 向量数据库加载完成 (table_name: {table_name})")
    print()
    
    # 构建AbstractForest
    print("构建AbstractForest...")
    abstract_forest, entity_to_abstract_map, entity_abstract_address_map = \
        build_abstract_forest_and_entity_mapping(
            vec_db=db,
            entities_list=entities_list,
            table_name=table_name
        )
    print(f"✓ AbstractForest构建完成，包含 {len(abstract_forest)} 个AbstractTree")
    print()
    
    # 分析Tree结构
    analyze_tree_structure(abstract_forest)
    
    # 分析父节点追溯（使用一些示例pair_ids）
    sample_pair_ids = []
    for tree in abstract_forest:
        nodes = tree.get_all_nodes()
        if nodes:
            # 取前几个节点的pair_id作为示例
            sample_pair_ids.extend([node.get_pair_id() for node in nodes[:3]])
    
    if sample_pair_ids:
        # 将列表切片转换为列表
        sample_pair_ids_list = list(sample_pair_ids[:15]) if len(sample_pair_ids) > 15 else list(sample_pair_ids)
        analyze_parent_expansion(abstract_forest, sample_pair_ids_list)


if __name__ == "__main__":
    main()


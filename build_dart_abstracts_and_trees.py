#!/usr/bin/env python
"""为DART数据集生成abstracts并建树"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

from rag_base.build_index import load_vec_db, build_index_on_chunks
from trag_tree.build import build_abstract_forest_and_entity_mapping
import json
import time

def main():
    print("=" * 80)
    print("DART数据集：生成Abstracts并建树")
    print("=" * 80)
    
    # 配置
    vec_db_key = "dart"
    # 使用JSON文件以保留source信息（用于按source分组建树）
    dataset_file = "./datasets/processed/dart.json"
    chunks_file = "./datasets/dart_chunks.txt"  # 备用
    entities_file = "./dart_entities_file.csv"
    
    # 优先使用JSON文件（能保留source信息）
    if os.path.exists(dataset_file):
        data_source = dataset_file
        print(f"✓ 使用JSON文件: {dataset_file}（保留source信息）")
    elif os.path.exists(chunks_file):
        data_source = chunks_file
        print(f"⚠ 使用txt文件: {chunks_file}（无法按source分组）")
    else:
        print(f"✗ 数据文件不存在: {dataset_file} 或 {chunks_file}")
        return
    
    if not os.path.exists(entities_file):
        print(f"✗ 实体文件不存在: {entities_file}")
        return
    
    print(f"\n1. 加载数据文件: {data_source}")
    print(f"2. 生成abstracts（每两个chunks生成1个abstract，使用并发API）")
    print(f"3. 构建向量数据库（按source分组）")
    print(f"4. 为每个source构建AbstractTree")
    print()
    
    start_time = time.time()
    
    # Step 1: 构建向量数据库（会自动生成abstracts）
    print("=" * 80)
    print("步骤1: 构建向量数据库并生成abstracts")
    print("=" * 80)
    
    print(f"正在从 {data_source} 加载chunks并生成abstracts...")
    print("注意：这将调用API生成abstracts，使用并发模式加速...")
    print("     每两个chunks生成1个abstract，每个source的abstracts会建一棵树")
    
    try:
        # load_vec_db会自动调用build_index_on_chunks，后者会调用expand_chunks_to_tree_nodes
        # expand_chunks_to_tree_nodes会：
        # 1. 保留所有raw chunks
        # 2. 每两个chunks生成1个abstract（tree_node）
        # 3. 如果数据有source字段，会按source分组
        # 4. 使用并发API调用加速
        
        vec_db = load_vec_db(vec_db_key, data_source)
        print(f"✓ 向量数据库构建完成，abstracts已生成")
        
        # 获取表名 - 从load_vec_db的内部映射获取，或从数据库获取
        table_name = None
        if hasattr(load_vec_db, '_db_table_map'):
            table_name = load_vec_db._db_table_map.get(id(vec_db))
        
        if not table_name:
            keys = vec_db.get_all_keys()
            table_name = keys[0] if keys else "default_table"
        
        print(f"✓ 表名: {table_name}")
        
        # 验证数据库内容
        try:
            count = vec_db.get_len(table_name)
            print(f"✓ 数据库记录数: {count}")
            
            # 统计abstracts和chunks
            all_data = vec_db.extract_data(table_name)
            abstracts = [m for _, m in all_data if m.get('type') == 'tree_node']
            raw_chunks = [m for _, m in all_data if m.get('type') == 'raw_chunk']
            print(f"  - Raw chunks: {len(raw_chunks)}")
            print(f"  - Abstracts (tree_nodes): {len(abstracts)}")
        except Exception as e:
            print(f"⚠ 验证数据库内容时出错: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"✗ 构建向量数据库失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: 读取实体列表
    print("\n" + "=" * 80)
    print("步骤2: 读取实体列表")
    print("=" * 80)
    
    entities_list = []
    try:
        with open(entities_file, 'r', encoding='utf-8') as f:
            import csv
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    entities_list.append(row[0].strip())
                    entities_list.append(row[1].strip())
        
        entities_list = list(set(entities_list))  # 去重
        print(f"✓ 读取到 {len(entities_list)} 个唯一实体")
        
    except Exception as e:
        print(f"✗ 读取实体文件失败: {e}")
        return
    
    # Step 3: 构建AbstractForest（为每个source建一棵树）
    print("\n" + "=" * 80)
    print("步骤3: 构建AbstractForest（为每个source建一棵树）")
    print("=" * 80)
    
    print("注意：这将调用API为每个source的abstracts建立层次关系，使用并发模式加速...")
    
    try:
        # 确保table_name已正确获取
        if not table_name:
            keys = vec_db.get_all_keys()
            table_name = keys[0] if keys else "default_table"
            print(f"  使用表名: {table_name}")
        
        abstract_forest, entity_to_abstract_map, entity_abstract_address_map = build_abstract_forest_and_entity_mapping(
            vec_db,
            entities_list,
            table_name=table_name  # 明确传递表名
        )
        
        print(f"✓ AbstractForest构建完成")
        print(f"  - AbstractTree数量: {len(abstract_forest)}")
        print(f"  - Entity到Abstract映射数量: {len(entity_to_abstract_map)}")
        
        # 显示每个Tree的信息
        for i, tree in enumerate(abstract_forest):
            root = tree.get_root()
            node_count = len(tree.get_all_nodes())
            print(f"  - Tree {i+1}: {node_count} 个abstracts, 根节点pair_id: {root.pair_id if root else 'N/A'}")
        
    except Exception as e:
        print(f"✗ 构建AbstractForest失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"✓ 全部完成！总耗时: {elapsed:.2f}秒")
    print("=" * 80)
    
    print("\n下一步：")
    print("1. 向量数据库已保存到: vec_db_cache/dart.db")
    print("2. AbstractForest已构建，可以在RAG中使用")
    print("3. 运行benchmark测试：")
    print("   python benchmark/run_benchmark.py \\")
    print("       --dataset ./datasets/processed/dart.json \\")
    print("       --vec-db-key dart \\")
    print("       --entities-file-name dart_entities_file \\")
    print("       --search-method 2 \\")
    print("       --max-samples 30")

if __name__ == "__main__":
    main()


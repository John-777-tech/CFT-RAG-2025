#!/usr/bin/env python3
"""
从新的实体列表和chunks文件构建AbstractForest
支持MedQA、DART、TriviaQA三个数据集
"""
import os
import sys
from dotenv import load_dotenv
from rag_base.build_index import load_vec_db
from trag_tree import build
from entity import ruler

load_dotenv()

def convert_entities_txt_to_csv(txt_file, csv_file):
    """
    将txt格式的实体列表转换为CSV格式
    txt格式：每行一个实体
    CSV格式：每行两列（subject, object），创建自引用关系
    """
    print(f"正在转换实体文件: {txt_file} -> {csv_file}")
    
    entities = []
    with open(txt_file, 'r', encoding='utf-8') as f:
        for line in f:
            entity = line.strip()
            if entity:
                entities.append(entity)
    
    # 创建CSV文件，每行一个实体对（自引用）
    # 格式：entity,entity（表示实体自身的关系）
    with open(csv_file, 'w', encoding='utf-8') as f:
        for entity in entities:
            # 创建自引用关系
            f.write(f"{entity},{entity}\n")
    
    print(f"✓ 转换完成：{len(entities)} 个实体")
    return entities

def build_forest_for_dataset(dataset_name, vec_db_key, entities_txt_file, entities_csv_file):
    """
    为指定数据集构建AbstractForest
    """
    print("=" * 80)
    print(f"为 {dataset_name} 数据集构建AbstractForest")
    print("=" * 80)
    
    # 1. 转换实体文件格式
    if not os.path.exists(entities_csv_file):
        if os.path.exists(entities_txt_file):
            convert_entities_txt_to_csv(entities_txt_file, entities_csv_file)
        else:
            print(f"✗ 实体文件不存在: {entities_txt_file}")
            return False
    else:
        print(f"✓ 实体CSV文件已存在: {entities_csv_file}")
    
    # 2. 加载向量数据库
    print(f"\n步骤1: 加载向量数据库 (key: {vec_db_key})...")
    try:
        vec_db = load_vec_db(vec_db_key, "vec_db_cache/")
        print(f"✓ 向量数据库加载完成")
    except Exception as e:
        print(f"✗ 加载向量数据库失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. 读取实体列表
    print(f"\n步骤2: 读取实体列表...")
    entities_list = set()
    try:
        with open(entities_csv_file, "r", encoding='utf-8') as csvfile:
            import csv as csv_module
            csvreader = csv_module.reader(csvfile, delimiter=',')
            for row in csvreader:
                if len(row) >= 2:
                    entities_list.add(row[0].strip())
                    entities_list.add(row[1].strip())
    except Exception as e:
        print(f"✗ 读取实体列表失败: {e}")
        return False
    
    print(f"✓ 读取到 {len(entities_list)} 个实体")
    
    # 4. 获取table_name
    print(f"\n步骤3: 获取向量数据库表名...")
    from rag_base import build_index
    db_id = id(vec_db)
    table_name = None
    if hasattr(build_index.load_vec_db, '_db_table_map'):
        table_name = build_index.load_vec_db._db_table_map.get(db_id)
    
    if table_name:
        print(f"✓ 表名: {table_name}")
    else:
        print("⚠ 未找到表名，使用默认值")
    
    # 5. 构建AbstractForest和实体映射
    print(f"\n步骤4: 构建AbstractForest和实体映射...")
    try:
        abstract_forest, entity_to_abstract_map, entity_abstract_address_map = build.build_abstract_forest_and_entity_mapping(
            vec_db,
            list(entities_list),
            table_name=table_name
        )
        
        # 统计信息
        total_abstracts = sum(len(tree.get_all_nodes()) for tree in abstract_forest)
        total_entity_mappings = sum(len(nodes) for nodes in entity_to_abstract_map.values())
        
        print(f"✓ AbstractForest构建完成:")
        print(f"  - AbstractTree数量: {len(abstract_forest)}")
        print(f"  - 总abstracts数量: {total_abstracts}")
        print(f"  - 实体映射数量: {total_entity_mappings}")
        print(f"  - 有映射的实体数量: {sum(1 for nodes in entity_to_abstract_map.values() if nodes)}")
        
        # 注意：Cuckoo Filter的更新已经在build_abstract_forest_and_entity_mapping函数内部完成
        
        return True
        
    except Exception as e:
        print(f"✗ 构建AbstractForest失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数：为三个数据集构建AbstractForest"""
    
    base_dir = "/Users/zongyikun/Downloads/CFT-RAG-2025-main"
    extracted_data_dir = os.path.join(base_dir, "extracted_data")
    
    datasets = [
        {
            "name": "MedQA",
            "vec_db_key": "medqa",
            "entities_txt": os.path.join(extracted_data_dir, "medqa_entities_list.txt"),
            "entities_csv": os.path.join(base_dir, "medqa_entities_file.csv"),
        },
        {
            "name": "DART",
            "vec_db_key": "dart",
            "entities_txt": os.path.join(extracted_data_dir, "dart_entities_list.txt"),
            "entities_csv": os.path.join(base_dir, "dart_entities_file.csv"),
        },
        {
            "name": "TriviaQA",
            "vec_db_key": "triviaqa",
            "entities_txt": os.path.join(extracted_data_dir, "triviaqa_entities_list.txt"),
            "entities_csv": os.path.join(base_dir, "triviaqa_entities_file.csv"),
        },
    ]
    
    print("=" * 80)
    print("为三个数据集构建AbstractForest")
    print("=" * 80)
    print()
    
    results = {}
    for dataset in datasets:
        success = build_forest_for_dataset(
            dataset["name"],
            dataset["vec_db_key"],
            dataset["entities_txt"],
            dataset["entities_csv"]
        )
        results[dataset["name"]] = success
        print()
    
    # 总结
    print("=" * 80)
    print("构建结果总结")
    print("=" * 80)
    for name, success in results.items():
        status = "✓ 成功" if success else "✗ 失败"
        print(f"  {name}: {status}")
    print("=" * 80)

if __name__ == "__main__":
    main()


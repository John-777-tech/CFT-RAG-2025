#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为TriviaQA构建AbstractForest和更新Cuckoo Filter
1. 重新提取实体（使用spacy）
2. 从向量数据库加载abstracts，按source_file分组
3. 为每个txt文件构建一个AbstractTree（使用LLM建立层级关系）
4. 构建AbstractForest
5. 建立entity→abstract映射并更新Cuckoo Filter
"""

import os
import sys
import shutil
from rag_base.build_index import load_vec_db
from trag_tree import build
from benchmark.extract_entities_and_chunks import build_entities_file_from_dataset
from build_forest_from_new_data import convert_entities_txt_to_csv

def main():
    print("=" * 80)
    print("TriviaQA: 构建AbstractForest和更新Cuckoo Filter")
    print("=" * 80)
    print()
    
    base_dir = os.getcwd()
    extracted_data_dir = os.path.join(base_dir, "extracted_data")
    
    # TriviaQA配置
    dataset_name = "TriviaQA"
    vec_db_key = "triviaqa"
    chunks_file = os.path.join(extracted_data_dir, "triviaqa_chunks.txt")
    entities_txt = os.path.join(extracted_data_dir, "triviaqa_entities_list.txt")
    entities_csv = os.path.join(base_dir, "triviaqa_entities_file.csv")
    
    # 步骤1: 重新提取实体（使用spacy）
    print("步骤1: 重新提取实体（使用spacy NER）...")
    print(f"  源文件: {chunks_file}")
    
    if not os.path.exists(chunks_file):
        print(f"  ✗ 错误: chunks文件不存在: {chunks_file}")
        return False
    
    # 删除旧的实体文件
    if os.path.exists(entities_txt):
        os.remove(entities_txt)
        print(f"  ✓ 已删除旧的实体列表文件")
    if os.path.exists(entities_csv):
        os.remove(entities_csv)
        print(f"  ✓ 已删除旧的实体CSV文件")
    
    # 读取chunks
    print(f"  正在读取chunks...")
    chunks = []
    with open(chunks_file, 'r', encoding='utf-8') as f:
        current_chunk = []
        for line in f:
            if line.startswith('# Chunk'):
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
            else:
                current_chunk.append(line.rstrip())
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
    
    print(f"  ✓ 读取了 {len(chunks):,} 个chunks")
    
    # 使用spacy提取实体
    print(f"  正在使用spacy NER提取实体（这可能需要一些时间）...")
    entities_output_path = entities_txt.replace('_entities_list.txt', '_entities_file.csv')
    entities_file = build_entities_file_from_dataset(
        chunks_file,
        entities_output_path,
        dataset_type="triviaqa",
        chunks=chunks
    )
    
    # 确保实体文件在正确位置
    if entities_file and os.path.exists(entities_file):
        if entities_file != entities_txt:
            os.makedirs(os.path.dirname(entities_txt) or '.', exist_ok=True)
            if os.path.exists(entities_txt):
                os.remove(entities_txt)
            shutil.move(entities_file, entities_txt)
            print(f"  ✓ 实体文件已移动到: {entities_txt}")
    
    if not os.path.exists(entities_txt):
        print(f"  ✗ 错误: 实体文件未生成: {entities_txt}")
        return False
    
    # 统计实体数量
    with open(entities_txt, 'r', encoding='utf-8') as f:
        entity_count = sum(1 for line in f if line.strip())
    print(f"  ✓ 提取了 {entity_count:,} 个唯一实体")
    
    # 转换实体文件格式为CSV
    print(f"  正在转换实体文件为CSV格式...")
    convert_entities_txt_to_csv(entities_txt, entities_csv)
    if os.path.exists(entities_csv):
        print(f"  ✓ 实体CSV文件已生成: {entities_csv}")
    else:
        print(f"  ✗ 错误: 实体CSV文件未生成")
        return False
    
    print()
    
    # 步骤2: 加载向量数据库
    print("步骤2: 加载向量数据库...")
    vec_db_path = f"vec_db_cache/{vec_db_key}.db"
    if not os.path.exists(vec_db_path):
        print(f"  ✗ 错误: 向量数据库不存在: {vec_db_path}")
        return False
    
    vec_db = load_vec_db(vec_db_key, "vec_db_cache/")
    print(f"  ✓ 向量数据库加载完成")
    
    # 获取表名
    from rag_base import build_index
    db_id = id(vec_db)
    table_name = None
    if hasattr(build_index.load_vec_db, '_db_table_map'):
        table_name = build_index.load_vec_db._db_table_map.get(db_id)
    if not table_name:
        keys = vec_db.get_all_keys()
        table_name = keys[0] if keys else "default_table"
    
    print(f"  使用表名: {table_name}")
    
    # 检查向量数据库中的abstracts
    print(f"  正在检查向量数据库内容...")
    all_data = vec_db.extract_data(table_name)
    chunks_in_db = 0
    abstracts_in_db = 0
    for vec, metadata in all_data:
        meta_dict = dict(metadata)
        if meta_dict.get("type") == "raw_chunk":
            chunks_in_db += 1
        elif meta_dict.get("type") == "tree_node":
            abstracts_in_db += 1
    
    print(f"  ✓ 向量数据库包含:")
    print(f"    - Chunks: {chunks_in_db:,} 个")
    print(f"    - Abstracts: {abstracts_in_db:,} 个")
    
    if abstracts_in_db == 0:
        print(f"  ✗ 错误: 向量数据库中没有abstracts，需要先生成abstracts")
        return False
    
    print()
    
    # 步骤3: 构建AbstractForest（按source_file分组，每个txt一个tree）
    print("步骤3: 构建AbstractForest（按source_file分组，每个txt文件一个tree）...")
    
    # 读取实体列表
    entities_list = []
    if os.path.exists(entities_txt):
        with open(entities_txt, 'r', encoding='utf-8') as f:
            for line in f:
                entity = line.strip()
                if entity:
                    entities_list.append(entity)
    else:
        print(f"  ✗ 错误: 实体列表文件不存在: {entities_txt}")
        return False
    
    print(f"  实体列表: {len(entities_list):,} 个实体")
    
    # 构建AbstractForest和entity映射
    print(f"  正在构建AbstractForest（使用LLM建立层级关系）...")
    abstract_forest, entity_to_abstract_map, entity_abstract_address_map = build.build_abstract_forest_and_entity_mapping(
        vec_db,
        entities_list,
        table_name=table_name
    )
    
    total_abstracts = sum(len(tree.get_all_nodes()) for tree in abstract_forest)
    total_entity_mappings = sum(len(nodes) for nodes in entity_to_abstract_map.values())
    
    print(f"  ✓ AbstractForest构建完成:")
    print(f"    - AbstractTree数量: {len(abstract_forest)}")
    print(f"    - 总abstracts数量: {total_abstracts:,}")
    print(f"    - 实体映射数量: {total_entity_mappings:,}")
    print(f"    - 有映射的实体数量: {sum(1 for nodes in entity_to_abstract_map.values() if nodes)}")
    
    print()
    
    # 步骤4: 保存AbstractForest缓存
    print("步骤4: 保存AbstractForest缓存...")
    cache_dir = "abstract_forest_cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"abstract_forest_{vec_db_key}.pkl")
    
    import pickle
    cached_data = {
        'abstract_forest': abstract_forest,
        'entity_to_abstract_map': entity_to_abstract_map,
        'entity_abstract_address_map': entity_abstract_address_map,
        'table_name': table_name
    }
    
    with open(cache_file, 'wb') as f:
        pickle.dump(cached_data, f)
    
    print(f"  ✓ AbstractForest缓存已保存: {cache_file}")
    
    print()
    print("=" * 80)
    print("TriviaQA构建完成！")
    print("=" * 80)
    print()
    print("总结:")
    print(f"  - Chunks: {len(chunks):,} 个")
    print(f"  - 实体: {entity_count:,} 个")
    print(f"  - Abstracts: {abstracts_in_db:,} 个（向量数据库中）")
    print(f"  - AbstractTrees: {len(abstract_forest)} 个")
    print(f"  - 总AbstractNodes: {total_abstracts:,} 个")
    print(f"  - 实体映射: {total_entity_mappings:,} 个")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


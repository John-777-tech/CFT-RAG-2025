#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为DART和MedQA构建AbstractForest和更新Cuckoo Filter
1. 提取chunks（如果还没有）
2. 提取实体（使用spacy）
3. 构建向量数据库（如果还没有）
4. 从向量数据库加载abstracts，按source_file分组
5. 为每个txt文件构建一个AbstractTree（使用LLM建立层级关系）
6. 构建AbstractForest
7. 建立entity→abstract映射并更新Cuckoo Filter
"""

import os
import sys
import shutil
from rag_base.build_index import load_vec_db, build_index_on_chunks, collect_chunks_from_file, collect_chunks_from_dir
from trag_tree import build
from benchmark.extract_entities_and_chunks import build_entities_file_from_dataset
from build_forest_from_new_data import convert_entities_txt_to_csv

def build_forest_for_dataset(dataset_name, vec_db_key, source_path, dataset_type, chunks_file, entities_txt, entities_csv):
    """
    为指定数据集构建AbstractForest
    """
    print("=" * 80)
    print(f"{dataset_name}: 构建AbstractForest和更新Cuckoo Filter")
    print("=" * 80)
    print()
    
    base_dir = os.getcwd()
    extracted_data_dir = os.path.join(base_dir, "extracted_data")
    
    # 步骤1: 提取chunks（如果还没有）
    print("步骤1: 提取chunks...")
    print(f"  源文件: {source_path}")
    
    if not os.path.exists(source_path):
        print(f"  ✗ 错误: 源文件不存在: {source_path}")
        return False
    
    chunks = []
    file_chunks_map = None
    
    if os.path.exists(chunks_file):
        print(f"  ✓ Chunks文件已存在: {chunks_file}")
        # 读取现有chunks
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
        # 尝试从模块级变量获取file_chunks_map
        file_chunks_map = None
        if os.path.isdir(source_path):
            if hasattr(collect_chunks_from_dir, '_file_chunks_map'):
                file_chunks_map = collect_chunks_from_dir._file_chunks_map.get(source_path)
        else:
            if hasattr(collect_chunks_from_file, '_file_chunks_map'):
                file_chunks_map = collect_chunks_from_file._file_chunks_map.get(source_path)
    else:
        print(f"  正在从源文件提取chunks...")
        if os.path.isdir(source_path):
            chunks = collect_chunks_from_dir(source_path)
            # 从模块级变量获取file_chunks_map
            if hasattr(collect_chunks_from_dir, '_file_chunks_map'):
                file_chunks_map = collect_chunks_from_dir._file_chunks_map.get(source_path)
            else:
                file_chunks_map = None
        else:
            chunks = collect_chunks_from_file(source_path)
            # 从模块级变量获取file_chunks_map
            if hasattr(collect_chunks_from_file, '_file_chunks_map'):
                file_chunks_map = collect_chunks_from_file._file_chunks_map.get(source_path)
            else:
                file_chunks_map = None
        
        # 保存chunks
        os.makedirs(os.path.dirname(chunks_file) or '.', exist_ok=True)
        with open(chunks_file, 'w', encoding='utf-8') as f:
            for i, chunk in enumerate(chunks):
                f.write(f"# Chunk {i}\n{chunk}\n\n")
        
        print(f"  ✓ 提取了 {len(chunks):,} 个chunks")
    
    if not chunks:
        print(f"  ✗ 错误: 没有提取到chunks")
        return False
    
    print()
    
    # 步骤2: 提取实体（使用spacy）
    print("步骤2: 提取实体（使用spacy NER）...")
    
    # 删除旧的实体文件
    if os.path.exists(entities_txt):
        os.remove(entities_txt)
        print(f"  ✓ 已删除旧的实体列表文件")
    if os.path.exists(entities_csv):
        os.remove(entities_csv)
        print(f"  ✓ 已删除旧的实体CSV文件")
    
    # 使用spacy提取实体
    print(f"  正在使用spacy NER提取实体...")
    entities_output_path = entities_txt.replace('_entities_list.txt', '_entities_file.csv')
    entities_file = build_entities_file_from_dataset(
        chunks_file,
        entities_output_path,
        dataset_type=dataset_type,
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
    
    # 步骤3: 构建向量数据库（如果还没有）
    print("步骤3: 构建向量数据库...")
    vec_db_path = f"vec_db_cache/{vec_db_key}.db"
    
    if os.path.exists(vec_db_path):
        print(f"  ✓ 向量数据库已存在: {vec_db_path}")
        vec_db = load_vec_db(vec_db_key, "vec_db_cache/")
        
        # 检查数据库内容
        from rag_base import build_index
        db_id = id(vec_db)
        table_name = None
        if hasattr(build_index.load_vec_db, '_db_table_map'):
            table_name = build_index.load_vec_db._db_table_map.get(db_id)
        if not table_name:
            keys = vec_db.get_all_keys()
            table_name = keys[0] if keys else "default_table"
        
        try:
            all_data = vec_db.extract_data(table_name)
            chunks_in_db = sum(1 for vec, meta in all_data if dict(meta).get("type") == "raw_chunk")
            abstracts_in_db = sum(1 for vec, meta in all_data if dict(meta).get("type") == "tree_node")
            
            print(f"  ✓ 向量数据库包含:")
            print(f"    - Chunks: {chunks_in_db:,} 个")
            print(f"    - Abstracts: {abstracts_in_db:,} 个")
            
            if chunks_in_db != len(chunks):
                print(f"  ⚠ 警告: 数据库中的chunks数量({chunks_in_db:,})与文件中的({len(chunks):,})不匹配")
                print(f"  正在重新构建向量数据库...")
                # 删除旧的数据库
                if os.path.isdir(vec_db_path):
                    shutil.rmtree(vec_db_path)
                else:
                    os.remove(vec_db_path)
                vec_db = None
            else:
                print(f"  ✓ Chunks数量匹配")
        except Exception as e:
            print(f"  ⚠ 警告: 无法读取向量数据库: {e}")
            print(f"  正在重新构建向量数据库...")
            # 删除旧的数据库
            if os.path.isdir(vec_db_path):
                shutil.rmtree(vec_db_path)
            else:
                if os.path.exists(vec_db_path):
                    os.remove(vec_db_path)
            vec_db = None
    else:
        vec_db = None
    
    if vec_db is None:
        print(f"  正在构建向量数据库...")
        os.makedirs("vec_db_cache", exist_ok=True)
        vec_db = build_index_on_chunks(chunks, target_dir=vec_db_path, file_chunks_map=file_chunks_map)
        print(f"  ✓ 向量数据库构建完成: {vec_db_path}")
    
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
    try:
        all_data = vec_db.extract_data(table_name)
        chunks_in_db = sum(1 for vec, meta in all_data if dict(meta).get("type") == "raw_chunk")
        abstracts_in_db = sum(1 for vec, meta in all_data if dict(meta).get("type") == "tree_node")
    except Exception as e:
        print(f"  ✗ 错误: 无法读取向量数据库: {e}")
        return False
    
    print(f"  ✓ 向量数据库包含:")
    print(f"    - Chunks: {chunks_in_db:,} 个")
    print(f"    - Abstracts: {abstracts_in_db:,} 个")
    
    if abstracts_in_db == 0:
        print(f"  ✗ 错误: 向量数据库中没有abstracts，需要先生成abstracts")
        return False
    
    print()
    
    # 步骤4: 构建AbstractForest（按source_file分组，每个txt一个tree）
    print("步骤4: 构建AbstractForest（按source_file分组，每个txt文件一个tree）...")
    
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
    
    # 步骤5: 保存AbstractForest缓存
    print("步骤5: 保存AbstractForest缓存...")
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
    print(f"{dataset_name}构建完成！")
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

def main():
    base_dir = os.getcwd()
    extracted_data_dir = os.path.join(base_dir, "extracted_data")
    
    datasets = [
        {
            "name": "DART",
            "vec_db_key": "dart",
            "source": "datasets/unified/dart-v1.1.1-full-dev.json",
            "dataset_type": "dart",
            "chunks_file": os.path.join(extracted_data_dir, "dart_chunks.txt"),
            "entities_txt": os.path.join(extracted_data_dir, "dart_entities_list.txt"),
            "entities_csv": os.path.join(base_dir, "dart_entities_file.csv"),
        },
        {
            "name": "MedQA",
            "vec_db_key": "medqa",
            "source": "datasets/unified/Med_data_clean/textbooks/en",  # 使用英文textbooks
            "dataset_type": "medqa",
            "chunks_file": os.path.join(extracted_data_dir, "medqa_chunks.txt"),
            "entities_txt": os.path.join(extracted_data_dir, "medqa_entities_list.txt"),
            "entities_csv": os.path.join(base_dir, "medqa_entities_file.csv"),
        },
    ]
    
    results = {}
    
    for dataset in datasets:
        print()
        print()
        success = build_forest_for_dataset(
            dataset["name"],
            dataset["vec_db_key"],
            dataset["source"],
            dataset["dataset_type"],
            dataset["chunks_file"],
            dataset["entities_txt"],
            dataset["entities_csv"]
        )
        results[dataset["name"]] = success
    
    print()
    print()
    print("=" * 80)
    print("构建结果总结")
    print("=" * 80)
    for name, success in results.items():
        status = "✓ 成功" if success else "✗ 失败"
        print(f"  {name}: {status}")
    print("=" * 80)
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


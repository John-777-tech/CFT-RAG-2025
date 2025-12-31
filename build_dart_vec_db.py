#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为DART生成abstracts并构建向量数据库
1. 读取DART的chunks
2. 调用API生成abstracts（每2个chunks生成1个abstract）
3. 构建向量数据库（包含chunks和abstracts）
"""

import os
import sys
import shutil

# 首先加载.env文件
from dotenv import load_dotenv
load_dotenv()

from rag_base.build_index import build_index_on_chunks, collect_chunks_from_file, load_vec_db

def main():
    print("=" * 80)
    print("DART: 生成abstracts并构建向量数据库")
    print("=" * 80)
    print()
    
    base_dir = os.getcwd()
    extracted_data_dir = os.path.join(base_dir, "extracted_data")
    
    # DART配置
    dataset_name = "DART"
    vec_db_key = "dart"
    source_path = "datasets/unified/dart-v1.1.1-full-dev.json"
    chunks_file = os.path.join(extracted_data_dir, "dart_chunks.txt")
    vec_db_path = f"vec_db_cache/{vec_db_key}.db"
    
    # 步骤1: 读取chunks
    print("步骤1: 读取chunks...")
    
    if os.path.exists(chunks_file):
        print(f"  ✓ 从文件读取chunks: {chunks_file}")
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
    else:
        print(f"  ✗ Chunks文件不存在，从源文件提取...")
        if not os.path.exists(source_path):
            print(f"  ✗ 错误: 源文件不存在: {source_path}")
            return False
        
        chunks = collect_chunks_from_file(source_path)
        # 获取file_chunks_map（用于DART的source分组）
        file_chunks_map = None
        if hasattr(collect_chunks_from_file, '_file_chunks_map'):
            file_chunks_map = collect_chunks_from_file._file_chunks_map.get(source_path)
        
        # 保存chunks
        os.makedirs(os.path.dirname(chunks_file) or '.', exist_ok=True)
        with open(chunks_file, 'w', encoding='utf-8') as f:
            for i, chunk in enumerate(chunks):
                f.write(f"# Chunk {i}\n{chunk}\n\n")
        
        print(f"  ✓ 提取了 {len(chunks):,} 个chunks")
    
    if not chunks:
        print(f"  ✗ 错误: 没有chunks")
        return False
    
    print()
    
    # 步骤2: 删除旧的向量数据库
    print("步骤2: 删除旧的向量数据库...")
    if os.path.exists(vec_db_path):
        if os.path.isdir(vec_db_path):
            shutil.rmtree(vec_db_path)
            print(f"  ✓ 已删除目录: {vec_db_path}")
        else:
            os.remove(vec_db_path)
            print(f"  ✓ 已删除文件: {vec_db_path}")
    else:
        print(f"  ✓ 向量数据库不存在，无需删除")
    
    print()
    
    # 步骤3: 生成abstracts并构建向量数据库
    print("步骤3: 生成abstracts并构建向量数据库...")
    print(f"  - 将调用LLM API生成abstracts（每2个chunks生成1个abstract）")
    print(f"  - 预计生成 {len(chunks) // 2:,} 个abstracts")
    print(f"  - 这可能需要一些时间...")
    print()
    
    # 获取file_chunks_map（如果之前没有获取）
    file_chunks_map = None
    if not file_chunks_map:
        if hasattr(collect_chunks_from_file, '_file_chunks_map'):
            file_chunks_map = collect_chunks_from_file._file_chunks_map.get(source_path)
    
    # 构建向量数据库（会自动生成abstracts）
    os.makedirs("vec_db_cache", exist_ok=True)
    vec_db = build_index_on_chunks(
        chunks, 
        batch_size=100,  # 批量处理大小
        target_dir=vec_db_path,
        file_chunks_map=file_chunks_map
    )
    
    print()
    print(f"  ✓ 向量数据库构建完成: {vec_db_path}")
    
    # 步骤4: 验证向量数据库
    print()
    print("步骤4: 验证向量数据库...")
    
    # 重新加载数据库以验证
    vec_db = load_vec_db(vec_db_key, "vec_db_cache/")
    
    from rag_base import build_index
    db_id = id(vec_db)
    table_name = None
    if hasattr(build_index.load_vec_db, '_db_table_map'):
        table_name = build_index.load_vec_db._db_table_map.get(db_id)
    if not table_name:
        keys = vec_db.get_all_keys()
        table_name = keys[0] if keys else "default_table"
    
    all_data = vec_db.extract_data(table_name)
    chunks_in_db = sum(1 for vec, meta in all_data if dict(meta).get("type") == "raw_chunk")
    abstracts_in_db = sum(1 for vec, meta in all_data if dict(meta).get("type") == "tree_node")
    
    print(f"  ✓ 向量数据库验证:")
    print(f"    - Chunks: {chunks_in_db:,} 个")
    print(f"    - Abstracts: {abstracts_in_db:,} 个")
    print(f"    - 总计: {chunks_in_db + abstracts_in_db:,} 个")
    
    # 检查数量是否匹配
    if chunks_in_db == len(chunks):
        print(f"    ✓ Chunks数量匹配")
    else:
        print(f"    ⚠ Chunks数量不匹配 (DB: {chunks_in_db:,} vs 文件: {len(chunks):,})")
    
    expected_abstracts = len(chunks) // 2
    if abstracts_in_db == expected_abstracts:
        print(f"    ✓ Abstracts数量正确 (每2个chunks生成1个abstract)")
    else:
        print(f"    ⚠ Abstracts数量异常 (期望: {expected_abstracts:,}, 实际: {abstracts_in_db:,})")
    
    print()
    print("=" * 80)
    print("DART向量数据库构建完成！")
    print("=" * 80)
    print()
    print("总结:")
    print(f"  - Chunks: {len(chunks):,} 个")
    print(f"  - Abstracts: {abstracts_in_db:,} 个")
    print(f"  - 向量数据库: {vec_db_path}")
    print()
    print("下一步: 可以运行 build_dart_medqa_forest.py 来构建AbstractForest")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


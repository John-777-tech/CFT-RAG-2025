#!/usr/bin/env python
"""检查DART数据集构建状态"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("DART数据集构建状态检查")
print("=" * 80)

# 1. 检查向量数据库
print("\n1. 向量数据库状态:")
vec_db_key = "dart"
cache_dir = "vec_db_cache/"
index_path = os.path.join(cache_dir, f"{vec_db_key}.db")

if os.path.exists(index_path):
    print(f"   ✓ 目录存在: {index_path}")
    files = os.listdir(index_path)
    if files:
        print(f"   ✓ 包含 {len(files)} 个文件")
        print(f"   文件列表: {', '.join(files[:5])}")
        
        # 尝试检查数据库内容
        try:
            from rag_base.build_index import load_vec_db
            db = load_vec_db(vec_db_key, cache_dir)
            keys = db.get_all_keys()
            if keys:
                table = keys[0]
                count = db.get_len(table)
                print(f"   ✓ 数据库可加载，记录数: {count}")
                
                # 统计abstracts和chunks
                all_data = db.extract_data(table)
                abstracts = [m for _, m in all_data if m.get('type') == 'tree_node']
                raw_chunks = [m for _, m in all_data if m.get('type') == 'raw_chunk']
                print(f"     - Raw chunks: {len(raw_chunks)}")
                print(f"     - Abstracts (tree_nodes): {len(abstracts)}")
            else:
                print("   ⚠ 数据库为空")
        except Exception as e:
            print(f"   ✗ 加载失败: {e}")
    else:
        print("   ⚠ 目录为空，数据库未构建")
else:
    print(f"   ✗ 数据库不存在: {index_path}")

# 2. 检查AbstractTree缓存
print("\n2. AbstractTree缓存状态:")
abstract_cache_dir = "abstract_cache"
if os.path.exists(abstract_cache_dir):
    print(f"   ✓ 缓存目录存在: {abstract_cache_dir}")
    cache_files = [f for f in os.listdir(abstract_cache_dir) if 'dart' in f.lower() and f.endswith('.pkl')]
    if cache_files:
        print(f"   ✓ 找到 {len(cache_files)} 个缓存文件")
        for f in cache_files[:3]:
            size = os.path.getsize(os.path.join(abstract_cache_dir, f))
            print(f"     - {f} ({size/1024:.1f} KB)")
    else:
        print("   ⚠ 未找到DART相关的缓存文件")
else:
    print(f"   ✗ 缓存目录不存在: {abstract_cache_dir}")

# 3. 检查Cuckoo Filter更新逻辑
print("\n3. Cuckoo Filter更新逻辑:")
try:
    from trag_tree.set_cuckoo_abstract_addresses import cuckoo_filter_module
    if cuckoo_filter_module:
        print("   ✓ Cuckoo Filter模块可用")
    else:
        print("   ⚠ Cuckoo Filter模块不可用（需要编译）")
except Exception as e:
    print(f"   ⚠ Cuckoo Filter模块检查失败: {e}")

# 4. 检查构建脚本
print("\n4. 构建脚本状态:")
build_script = "build_dart_abstracts_and_trees.py"
if os.path.exists(build_script):
    print(f"   ✓ 构建脚本存在: {build_script}")
    print(f"   运行命令: python {build_script}")
else:
    print(f"   ✗ 构建脚本不存在: {build_script}")

print("\n" + "=" * 80)
print("总结:")
print("=" * 80)

# 总结
db_exists = os.path.exists(index_path) and os.listdir(index_path) if os.path.exists(index_path) else False
cache_exists = os.path.exists(abstract_cache_dir) and any('dart' in f.lower() for f in os.listdir(abstract_cache_dir)) if os.path.exists(abstract_cache_dir) else False

if db_exists and cache_exists:
    print("✓ 向量数据库和AbstractTree都已构建")
    print("✓ Cuckoo Filter会在运行benchmark时自动更新（如果使用search_method=7）")
elif db_exists:
    print("✓ 向量数据库已构建")
    print("⚠ AbstractTree缓存未找到，需要运行构建脚本")
elif cache_exists:
    print("⚠ 向量数据库未构建")
    print("✓ AbstractTree缓存存在")
else:
    print("✗ 向量数据库和AbstractTree都未构建")
    print("  需要运行: python build_dart_abstracts_and_trees.py")

print("\n注意：Cuckoo Filter的更新发生在build_abstract_forest_and_entity_mapping函数中")
print("     如果使用search_method=7（Cuckoo Filter），会在构建AbstractTree后自动更新")


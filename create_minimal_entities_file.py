#!/usr/bin/env python
"""创建最小实体文件（用于测试）"""

import csv
import sys

def create_minimal_entities_file(output_path, num_entities=10):
    """创建一个最小的实体文件用于测试"""
    
    # 创建简单的层次结构
    entities = []
    
    # 根节点
    root = "root"
    
    # 创建一些测试实体
    for i in range(num_entities):
        entity_name = f"entity_{i+1}"
        entities.append([entity_name, root])
    
    # 添加一些子实体
    for i in range(num_entities // 2):
        child_name = f"child_{i+1}"
        parent_name = f"entity_{i+1}"
        entities.append([child_name, parent_name])
    
    # 写入CSV文件
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for entity_pair in entities:
            writer.writerow(entity_pair)
    
    print(f"✓ 已创建最小实体文件: {output_path}")
    print(f"  包含 {len(entities)} 个实体关系")
    print()
    print("注意：这是一个测试文件，实际使用需要从真实数据集中提取实体关系。")
    print("实体文件格式：每行两个字段（用逗号分隔），表示父子关系（子实体,父实体）")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        output_path = "aeslc_entities_file.csv"
    
    create_minimal_entities_file(output_path)
    print(f"\n文件已创建: {output_path}")
    print("现在可以运行 Graph RAG 了。")




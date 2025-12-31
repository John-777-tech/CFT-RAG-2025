#!/usr/bin/env python
"""检查实体文件是否存在，如果不存在则提供解决方案"""

import os
import sys

def check_entities_file(entities_file_name):
    """检查实体文件是否存在"""
    file_path = f"{entities_file_name}.csv"
    
    print("=" * 70)
    print("实体文件检查")
    print("=" * 70)
    print()
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    print()
    
    # 检查文件是否存在
    if os.path.exists(file_path):
        print(f"✓ 文件存在: {file_path}")
        file_size = os.path.getsize(file_path)
        print(f"  文件大小: {file_size} 字节")
        
        # 检查文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"  行数: {len(lines)}")
                
                if len(lines) > 0:
                    print(f"  前3行示例:")
                    for i, line in enumerate(lines[:3], 1):
                        print(f"    {i}. {line.strip()}")
        except Exception as e:
            print(f"  ⚠️ 读取文件时出错: {e}")
        
        return True
    else:
        print(f"✗ 文件不存在: {file_path}")
        print()
        print("解决方案:")
        print("1. 检查文件名是否正确")
        print("2. 确保文件在项目根目录")
        print("3. 如果文件不存在，需要生成实体文件")
        print()
        
        # 检查是否有其他实体文件
        print("当前目录中的实体文件:")
        csv_files = [f for f in os.listdir('.') if f.endswith('_entities_file.csv') or f.endswith('entities_file.csv')]
        if csv_files:
            for f in csv_files:
                print(f"  - {f}")
        else:
            print("  未找到实体文件")
        
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        entities_file_name = sys.argv[1]
    else:
        entities_file_name = "aeslc_entities_file"
    
    exists = check_entities_file(entities_file_name)
    sys.exit(0 if exists else 1)




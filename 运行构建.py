#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建Abstract树并更新Cuckoo Filter
双击此文件即可运行（或使用python3运行）
"""
import sys
import os
from pathlib import Path

# 设置项目路径
BASE_DIR = Path(__file__).parent
os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))

# 导入构建函数
from build_abstract_and_cuckoo import main

# 数据集列表
datasets = ['medqa', 'dart', 'triviaqa']

print("=" * 80)
print("构建Abstract树并更新Cuckoo Filter")
print("=" * 80)
print()

for dataset in datasets:
    print()
    print("=" * 80)
    print(f"正在构建 {dataset.upper()} 数据集...")
    print("=" * 80)
    print()
    
    # 设置命令行参数
    sys.argv = ['build_abstract_and_cuckoo.py', '--dataset', dataset]
    
    try:
        main()
        print(f"\n✓ {dataset.upper()} 数据集构建成功！")
    except Exception as e:
        print(f"\n✗ {dataset.upper()} 数据集构建失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n继续构建下一个数据集...")
    
    print()

print()
print("=" * 80)
print("所有数据集构建完成！")
print("=" * 80)



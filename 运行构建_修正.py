#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建Abstract树并更新Cuckoo Filter
使用python310_arm环境运行
"""
import sys
import os
from pathlib import Path

# 设置项目路径
BASE_DIR = Path(__file__).parent
os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))

print("检查Python环境...")
print(f"Python路径: {sys.executable}")
print(f"Python版本: {sys.version}")
print()

# 检查必要的模块
try:
    import lab_1806_vec_db
    print(f"✓ lab_1806_vec_db 已安装")
except ImportError:
    print("✗ lab_1806_vec_db 未安装")
    print("请使用python310_arm环境运行：")
    print("/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 运行构建_修正.py")
    sys.exit(1)

try:
    import spacy
    print(f"✓ spacy 已安装")
except ImportError:
    print("✗ spacy 未安装")
    sys.exit(1)

print()

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



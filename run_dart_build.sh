#!/bin/bash
# DART数据集：生成Abstracts并建树

cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# 激活conda环境
source ~/opt/anaconda3/etc/profile.d/conda.sh
conda activate python310_arm

# 删除旧的数据库（如果存在）
if [ -d "vec_db_cache/dart.db" ]; then
    echo "删除旧的数据库..."
    rm -rf vec_db_cache/dart.db
fi

# 运行构建脚本
echo "开始构建DART向量数据库和AbstractTree..."
python build_dart_abstracts_and_trees.py


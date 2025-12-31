# 手动运行构建脚本指南

由于终端环境问题，请在你的**终端应用**（Terminal.app）中手动运行以下命令：

## 方法1：使用简单脚本（推荐）

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
./build_cuckoo_simple.sh
```

## 方法2：逐个运行

在你的终端中运行：

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# MedQA数据集
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 build_abstract_and_cuckoo.py --dataset medqa

# DART数据集
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 build_abstract_and_cuckoo.py --dataset dart

# TriviaQA数据集
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 build_abstract_and_cuckoo.py --dataset triviaqa
```

## 方法3：使用Python脚本

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 execute_build.py
```

## 如果遇到权限问题

```bash
chmod +x build_cuckoo_simple.sh
```

## 注意事项

- 确保在项目根目录运行命令
- 确保Python环境路径正确
- 构建过程可能需要一些时间，请耐心等待



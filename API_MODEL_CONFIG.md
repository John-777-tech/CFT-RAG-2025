# API 模型配置说明

## 问题描述

错误信息显示：
```
Error code: 404
The model or endpoint seed1.6 does not exist or you do not have access to it.
```

这说明代码尝试使用 `seed1.6` 模型，但该模型在ARK API中不存在。

## 模型配置方式

### 1. 默认模型

代码中的默认模型是 **`ge2.5-pro`**（在 `rag_base/rag_complete.py` 的 `get_model_name()` 函数中定义）：

```python
def get_model_name():
    return os.getenv("MODEL_NAME") or "ge2.5-pro"
```

### 2. 通过环境变量配置

可以通过设置 `MODEL_NAME` 环境变量来指定模型：

#### 方式1：在 `.env` 文件中配置（推荐）

在项目根目录的 `.env` 文件中添加：

```bash
# ARK API 配置
ARK_API_KEY=your_api_key_here
BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# 模型名称配置
MODEL_NAME=ge2.5-pro
```

#### 方式2：在命令行中设置

```bash
export MODEL_NAME=ge2.5-pro
python benchmark/run_benchmark.py ...
```

### 3. 支持的模型名称

根据ARK API，常用的模型名称包括：

- **`ge2.5-pro`** - 默认推荐（通用能力强）
- **`ge2.5-flash`** - 快速版本
- **`ge2.5-flash-lite`** - 轻量快速版本
- **`ge3-pro-preview`** - 预览版本
- **`ep-20241101151030-lfwks`** - 特定endpoint（需要你有访问权限）

**注意**：`seed1.6` 不是有效的模型名称，会导致404错误。

## 修复步骤

### 步骤1：检查 `.env` 文件

检查项目根目录的 `.env` 文件，确保 `MODEL_NAME` 设置正确：

```bash
# 如果 MODEL_NAME=seed1.6，需要改为：
MODEL_NAME=ge2.5-pro
```

### 步骤2：如果没有 `.env` 文件

创建 `.env` 文件：

```bash
# 在项目根目录创建 .env 文件
cat > .env << EOF
ARK_API_KEY=your_api_key_here
BASE_URL=https://ark.cn-beijing.volces.com/api/v3
MODEL_NAME=ge2.5-pro
EOF
```

### 步骤3：验证配置

运行以下命令验证模型配置：

```python
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
model_name = os.getenv('MODEL_NAME') or 'ge2.5-pro'
print(f'当前配置的模型: {model_name}')
"
```

## 代码中的模型使用位置

### 1. `rag_base/rag_complete.py`

- `get_model_name()` 函数：获取模型名称
- `rag_complete()` 函数：使用模型进行生成
- `augment_prompt()` 函数：默认参数 `model_name="gpt-3.5-turbo"`（但会被 `get_model_name()` 覆盖）

### 2. API调用位置

在 `rag_complete()` 函数中：

```python
# 使用ARK API配置
api_key = os.environ.get("ARK_API_KEY") or os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("BASE_URL") or "https://ark.cn-beijing.volces.com/api/v3"

# 获取模型名称
model_name = model_name or get_model_name()  # 默认使用 ge2.5-pro

# ARK API调用
if is_ark_api:
    response = client.responses.create(
        model=model_name,  # 这里使用配置的模型名称
        ...
    )
```

## 常见问题

### Q1: 如何知道哪些模型可用？

A: 查看ARK API文档，或联系ARK API服务提供商获取可用模型列表。

### Q2: 可以使用OpenAI的模型吗？

A: 可以，但需要：
1. 设置 `BASE_URL` 为 OpenAI 的API地址（或留空使用默认）
2. 设置 `OPENAI_API_KEY`
3. 设置 `MODEL_NAME` 为 OpenAI 模型名称（如 `gpt-3.5-turbo`, `gpt-4` 等）

### Q3: 如何为不同的benchmark使用不同的模型？

A: 可以在运行benchmark前临时设置环境变量：

```bash
MODEL_NAME=ge2.5-flash python benchmark/run_benchmark.py ...
```

## 完整配置示例

### `.env` 文件示例

```bash
# ARK API配置
ARK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# 模型配置
MODEL_NAME=ge2.5-pro

# 可选：OpenAI配置（如果使用OpenAI API）
# OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
# BASE_URL=https://api.openai.com/v1

# 嵌入模型配置
EMBED_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# HuggingFace镜像（可选）
HF_ENDPOINT=https://hf-mirror.com
```

## 快速修复命令

如果遇到 `seed1.6` 错误，运行：

```bash
# 检查当前配置
grep MODEL_NAME .env 2>/dev/null || echo "MODEL_NAME not found in .env"

# 修复配置（如果存在错误的配置）
sed -i.bak 's/MODEL_NAME=seed1.6/MODEL_NAME=ge2.5-pro/' .env

# 或者直接添加/更新配置
echo "MODEL_NAME=ge2.5-pro" >> .env
```




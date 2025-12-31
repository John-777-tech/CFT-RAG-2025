# 如何分享代码仓库

## 仓库信息

**GitHub仓库地址**：
```
https://github.com/John-777-tech/CFT-RAG-2025
```

## 分享方式

### 方式1：直接分享仓库链接（最简单）

直接发送GitHub仓库链接给其他人：

```
https://github.com/John-777-tech/CFT-RAG-2025
```

对方可以：
- 在浏览器中查看代码
- 点击 "Code" 按钮下载ZIP
- 使用Git克隆仓库

### 方式2：使用Git克隆（推荐）

告诉对方使用以下命令克隆仓库：

```bash
git clone https://github.com/John-777-tech/CFT-RAG-2025.git
cd CFT-RAG-2025
```

### 方式3：分享特定版本/标签

如果想让对方使用特定版本，可以创建标签：

```bash
# 创建标签
git tag -a v1.0.0 -m "CFT-RAG-2025 v1.0.0"
git push origin v1.0.0
```

然后分享：
```
https://github.com/John-777-tech/CFT-RAG-2025/releases/tag/v1.0.0
```

### 方式4：分享特定分支

如果代码在特定分支上：

```bash
# 查看所有分支
git branch -a

# 分享特定分支
git clone -b <branch-name> https://github.com/John-777-tech/CFT-RAG-2025.git
```

## 分享内容建议

### 1. 基本信息

```
项目名称：CFT-RAG-2025
仓库地址：https://github.com/John-777-tech/CFT-RAG-2025
描述：An Entity Tree Based Retrieval Augmented Generation Algorithm With Cuckoo Filter
```

### 2. 快速开始指南

告诉对方需要：

1. **克隆仓库**：
```bash
git clone https://github.com/John-777-tech/CFT-RAG-2025.git
cd CFT-RAG-2025
```

2. **安装依赖**：
```bash
pip install -r requirements.txt
```

3. **配置环境变量**：
```bash
cp .env.example .env
# 编辑 .env 文件，添加API密钥等
```

4. **运行示例**：
```bash
python main.py --search-method 0
```

### 3. 重要文件说明

告诉对方这些重要文件：

- `README.md` - 项目说明和快速开始
- `DATASET_RUN_COMMANDS.md` - 数据集运行命令
- `API_MODEL_CONFIG.md` - API模型配置说明
- `EVALUATION_SCRIPT_GUIDE.md` - 评估脚本使用指南
- `FIX_GRAPH_RAG_ENTITY_FILE.md` - Graph RAG实体文件问题解决
- `ENTITY_RELATIONSHIP_EXTRACTION.md` - 实体关系提取说明

### 4. 常见问题

提醒对方可能遇到的问题：

1. **实体文件缺失**：参考 `FIX_GRAPH_RAG_ENTITY_FILE.md`
2. **API模型配置**：参考 `API_MODEL_CONFIG.md`
3. **数据集下载**：参考 `DATASET_DOWNLOAD_GUIDE_FINAL.md`
4. **评估脚本使用**：参考 `EVALUATION_SCRIPT_GUIDE.md`

## 分享模板

你可以直接复制以下内容分享：

---

### CFT-RAG-2025 代码仓库

**GitHub地址**：https://github.com/John-777-tech/CFT-RAG-2025

**项目简介**：
CFT-RAG是一个基于实体树的检索增强生成算法，使用Cuckoo Filter进行加速。

**快速开始**：

1. 克隆仓库：
```bash
git clone https://github.com/John-777-tech/CFT-RAG-2025.git
cd CFT-RAG-2025
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境：
```bash
cp .env.example .env
# 编辑 .env 添加API密钥
```

4. 运行示例：
```bash
python main.py --search-method 0
```

**重要文档**：
- `README.md` - 完整使用说明
- `DATASET_RUN_COMMANDS.md` - 数据集运行命令
- `API_MODEL_CONFIG.md` - API配置说明
- `EVALUATION_SCRIPT_GUIDE.md` - 评估脚本指南

**遇到问题？** 查看项目中的 `*.md` 文档，或提交Issue。

---

## 权限设置

### 公开仓库（Public）

如果仓库是公开的，任何人都可以：
- 查看代码
- 克隆仓库
- Fork仓库
- 提交Issue

### 私有仓库（Private）

如果仓库是私有的，需要：
1. 添加协作者（Settings → Collaborators）
2. 或者使用GitHub邀请链接

**添加协作者步骤**：
1. 进入仓库：https://github.com/John-777-tech/CFT-RAG-2025
2. 点击 "Settings"
3. 点击 "Collaborators"
4. 点击 "Add people"
5. 输入对方的GitHub用户名或邮箱
6. 发送邀请

## 最佳实践

1. **保持README更新**：确保README包含最新信息
2. **添加LICENSE**：如果允许他人使用，添加许可证文件
3. **创建Release**：重要版本创建Release，方便分享
4. **文档完善**：确保关键文档完整
5. **Issue模板**：创建Issue模板，方便他人报告问题

## 检查清单

分享前确认：
- [ ] README.md 内容完整
- [ ] 代码可以正常运行
- [ ] 依赖文件（requirements.txt）存在
- [ ] 环境变量示例文件（.env.example）存在
- [ ] 重要文档已更新
- [ ] 仓库权限设置正确（Public/Private）


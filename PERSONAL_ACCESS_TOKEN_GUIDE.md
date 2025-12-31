# Personal Access Token (PAT) 完整指南

## 什么是Personal Access Token？

Personal Access Token（个人访问令牌，简称PAT）是GitHub提供的一种安全认证方式，用于替代密码进行Git操作。

### 为什么GitHub不再使用密码？

- **安全性**：Token可以设置特定权限，即使泄露也只会影响特定范围
- **可控性**：可以随时撤销，设置过期时间
- **追踪性**：可以知道哪个token在什么时候做了什么操作

---

## 如何创建Personal Access Token

### 步骤1：访问Token设置页面

1. 登录GitHub
2. 点击右上角头像
3. 选择 **Settings**
4. 左侧菜单找到 **Developer settings**
5. 点击 **Personal access tokens**
6. 选择 **Tokens (classic)**

或者直接访问：https://github.com/settings/tokens

### 步骤2：生成新Token

1. 点击 **"Generate new token"** 按钮
2. 选择 **"Generate new token (classic)"**

### 步骤3：配置Token

**Note（备注）**：
- 起一个容易识别的名字，例如：
  - `RAG项目上传`
  - `MacBook命令行访问`
  - `CFT-RAG开发`

**Expiration（过期时间）**：
- `No expiration`：永不过期（不推荐）
- `90 days`：90天后过期（推荐）
- `30 days`：30天后过期
- `Custom`：自定义日期

**Select scopes（选择权限）**：
对于上传代码到仓库，至少需要勾选：
- ✅ **`repo`** - 完整仓库访问权限（包括私有仓库）
  - 包括：代码读取、写入、删除等所有操作

其他常用权限（根据需要勾选）：
- `workflow` - GitHub Actions权限
- `read:org` - 读取组织信息
- `gist` - Gist操作

### 步骤4：生成并复制Token

1. 滚动到页面底部
2. 点击 **"Generate token"** 绿色按钮
3. **重要**：立即复制token（类似这样的格式：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）
   - ⚠️ Token只显示一次，关闭页面后无法再次查看
   - 如果忘记，只能删除重新生成

### 步骤5：保存Token（重要）

- 将token保存到安全的地方（密码管理器、安全笔记等）
- 不要在代码中硬编码token
- 不要分享给他人

---

## 如何使用Token

### 在Git推送时使用

当执行 `git push` 时：

```bash
git push -u origin main
```

会提示输入：
- **Username**: `John-777-tech`（你的GitHub用户名）
- **Password**: 粘贴你的Personal Access Token（不是GitHub密码！）

### macOS钥匙串自动保存

在macOS上，第一次输入后，系统会询问是否保存到钥匙串：
- 选择 **"总是允许"** 或 **"允许"**
- 之后就不需要再输入了

### 查看已保存的凭证

如果忘记是否保存过，可以查看：

```bash
# 查看Git凭证配置
git config --global credential.helper

# 查看macOS钥匙串中的GitHub凭证
# 打开"钥匙串访问"应用，搜索"github"
```

---

## Token格式示例

Personal Access Token通常长这样：

```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

- 以 `ghp_` 开头
- 后面是一串随机字符
- 长度约40-50个字符

---

## 安全性建议

### ✅ 推荐做法

1. **设置合理的过期时间**：不要设置"永不过期"
2. **最小权限原则**：只勾选必需的权限
3. **定期轮换**：每3-6个月生成新的token
4. **安全存储**：使用密码管理器保存
5. **及时撤销**：不使用的token及时删除

### ❌ 不要做的事

1. ❌ 不要将token提交到Git仓库
2. ❌ 不要分享token给他人
3. ❌ 不要在公开场合（如截图、文档）暴露token
4. ❌ 不要使用过高的权限（如admin权限）
5. ❌ 不要在多个项目共享同一个token

---

## 常见问题

### Q1: Token和密码有什么区别？

| 特性 | 密码 | Personal Access Token |
|------|------|---------------------|
| 用途 | 登录GitHub网站 | Git命令行操作 |
| 权限 | 完整账户权限 | 可设置特定权限 |
| 撤销 | 需要改密码 | 可以单独撤销 |
| 过期 | 永久有效 | 可设置过期时间 |
| 安全性 | 一旦泄露风险高 | 权限受限，更安全 |

### Q2: 如果token泄露了怎么办？

1. 立即访问：https://github.com/settings/tokens
2. 找到泄露的token
3. 点击 **"Revoke"（撤销）**
4. 生成新的token替换

### Q3: 如何查看所有token？

访问：https://github.com/settings/tokens

可以查看：
- 所有token列表
- 每个token的权限
- 最后使用时间
- 创建时间

### Q4: Token在哪里使用？

- Git命令行操作（push, pull, clone等）
- API调用
- 第三方应用授权

### Q5: 忘记保存token了怎么办？

只能重新生成新的token，旧的无法找回。

---

## 快速创建指南（截图步骤）

```
GitHub网站
  ↓
点击头像 → Settings
  ↓
左侧菜单 → Developer settings
  ↓
Personal access tokens → Tokens (classic)
  ↓
Generate new token → Generate new token (classic)
  ↓
填写Note → 选择过期时间 → 勾选repo权限
  ↓
Generate token → 复制token（立即保存！）
```

---

## 总结

1. **Personal Access Token是GitHub的安全认证方式**
2. **创建地址**：https://github.com/settings/tokens
3. **必需权限**：至少勾选 `repo`
4. **使用方法**：在Git推送时，Password处粘贴token
5. **安全保存**：复制后立即保存到安全位置

现在你可以去创建token了！创建好后，就可以使用 `git push -u origin main` 上传代码了。





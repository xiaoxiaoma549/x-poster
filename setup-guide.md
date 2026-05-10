# X 发推 — GitHub Actions 方案 搭建指南

## 你需要的东西

- GitHub 账号（你应该有）
- X 账号（已有）

## 步骤

### 1. 创建 GitHub 仓库

打开 https://github.com/new

- 仓库名: `x-poster`（或任何你喜欢的）
- 公开/私有都可以
- 勾选 "Add a README" 或不勾选都行
- 点创建

### 2. 推代码

```bash
cd ~/.hermes/projects/x-poster
git init
git add .
git commit -m "init: X posting via GitHub Actions"
git remote add origin https://github.com/<你的用户名>/x-poster.git
git branch -M main
git push -u origin main
```

### 3. 添加 GitHub Secrets

打开仓库 → Settings → Secrets and variables → Actions

添加以下 Secret:

| Secret 名 | 值 |
|:----------|:----|
| `X_AUTH_TOKEN` | `twitter_cookies.json` 里的 `auth_token` |
| `X_CT0` | `twitter_cookies.json` 里的 `ct0` |
| `X_KDT` | `twitter_cookies.json` 里的 `kdt`（可选） |

Cookie 文件在 `D:\hermes-overseas\twitter_cookies.json`
用 `cat /mnt/d/hermes-overseas/twitter_cookies.json` 查看。

### 4. 生成 GitHub PAT

打开 https://github.com/settings/tokens

- 点 "Generate new token (classic)"
- 勾选 `repo` 和 `workflow`
- 生成后复制 token 值（只显示一次！）

### 5. 配置 WSL 触发脚本

```bash
cd ~/.hermes/projects/x-poster
cat > .env << 'EOF'
GITHUB_TOKEN=<刚生成的PAT>
GITHUB_REPO=<你的用户名>/x-poster
EOF
chmod 600 .env
chmod +x trigger-x-post.sh
```

### 6. 测试

```bash
./trigger-x-post.sh "GitHub Actions 发推测试 ✅ Runner 在海外直连，零代理配置"
```

去 https://github.com/<你的用户名>/x-poster/actions 看运行日志。

## 集成到温差管线

在 `daily-publish` 或 `fermentation-track` 的 cron 中，发完头条/知乎后追加一行：

```bash
cd ~/.hermes/projects/x-poster && bash trigger-x-post.sh "推文内容"
```

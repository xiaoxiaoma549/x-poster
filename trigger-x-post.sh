#!/bin/bash
# WSL 侧触发 GitHub Actions 发推
# 用法: ./trigger-x-post.sh "推文内容"
#
# 前置条件:
#   1. 在 GitHub 生成 PAT (repo + workflow 权限)
#   2. 写入 .env 文件: GITHUB_TOKEN=xxx  GITHUB_REPO=你的用户名/仓库名

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ 找不到 $ENV_FILE"
    echo "   里面要放:"
    echo "   GITHUB_TOKEN=你的PAT"
    echo "   GITHUB_REPO=用户名/仓库名"
    exit 1
fi

source "$ENV_FILE"

if [ -z "$1" ]; then
    echo "用法: ./trigger-x-post.sh \"推文内容\""
    exit 1
fi

TWEET_TEXT="$1"

echo "⏳ 触发 GitHub Actions ..."

curl -s -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/$GITHUB_REPO/actions/workflows/x-post.yml/dispatches" \
  -d "$(jq -n --arg text "$TWEET_TEXT" '{"ref":"main","inputs":{"tweet_text":$text}}')"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 触发成功！推文将在几秒后发出"
    echo "   查看: https://github.com/$GITHUB_REPO/actions"
else
    echo "❌ 触发失败 (exit=$EXIT_CODE)"
    echo "   检查 GITHUB_TOKEN 和 GITHUB_REPO 是否正确"
fi

exit $EXIT_CODE

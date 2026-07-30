#!/bin/sh
# Trỏ git hooks vào scripts/hooks (thư mục CÓ trong repo, khác .git/hooks
# vốn không commit được nên mỗi máy clone lại mất hook).
set -e
cd "$(dirname "$0")/.."
chmod +x scripts/hooks/*
git config core.hooksPath scripts/hooks
echo "OK — core.hooksPath = scripts/hooks"
echo "Kiểm tra: git config --get core.hooksPath"

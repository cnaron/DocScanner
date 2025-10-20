#!/usr/bin/env bash
set -euo pipefail

APP_NAME="DocScanner"
PYTHON_BIN="python3"

# 1) venv
if [ ! -d ".venv" ]; then
  echo "▶ 创建虚拟环境 .venv"
  $PYTHON_BIN -m venv .venv
fi
source .venv/bin/activate

# 2) 依赖
echo "▶ 安装依赖"
pip install --upgrade pip wheel setuptools
# 原项目依赖
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi
# PyTorch（CPU/MPS 通用轮子）
pip install torch torchvision torchaudio
# 打包与下载工具
pip install pyinstaller gdown

# 3) 预训练模型（自动下载到 model_pretrained/）
echo "▶ 下载预训练模型（若已存在则跳过）"
mkdir -p model_pretrained
if [ -z "$(ls -A model_pretrained || true)" ]; then
  gdown --fuzzy --folder "https://drive.google.com/drive/folders/1W1_DJU8dfEh6FqDYqFQ7ypR38Z8c5r4D" -O model_pretrained
fi
echo "当前模型文件："
ls -lah model_pretrained

# 4) 确保运行时目录存在（避免 --add-data 报错）
mkdir -p distorted rectified app

# 5) 打包（macOS 上 --add-data 用冒号分隔 src:dst）
echo "▶ 使用 PyInstaller 打包 .app"
pyinstaller --noconfirm --windowed \
  --name "${APP_NAME}" \
  --add-data "model_pretrained:model_pretrained" \
  --add-data "inference.py:." \
  --add-data "distorted:distorted" \
  --add-data "rectified:rectified" \
  --add-data "app:app" \
  --hidden-import torch \
  app/main.py

# 6) 产物说明与压缩
echo "▶ 生成 ZIP 包"
cd dist
rm -f ../DocScanner-mac.zip
zip -r ../DocScanner-mac.zip "${APP_NAME}.app"
cd ..

echo "✅ 完成：dist/${APP_NAME}.app 与 DocScanner-mac.zip 已生成"
echo "提示：首次运行若提示来自未识别开发者，可在“系统设置 → 隐私与安全性”允许打开。"

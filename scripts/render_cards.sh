#!/bin/sh
# 重出全部卡片：改 gen.py 后运行本脚本。
# CHECK=1 ./render.sh 只测内容高度是否溢出，不出图；带卡片名只出单张，如 ./render.sh cover。
# 溢出检查需要 Pillow，先确认所选 Python 能 import PIL；出图本身不需要。
set -e
cd "$(dirname "$0")"
"${PY:-python3}" gen.py "$@"

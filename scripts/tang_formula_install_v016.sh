#!/usr/bin/env bash
set -euo pipefail
ROOT="$HOME/projects/stem-mentor-formula-v016"
mkdir -p "$ROOT"
if [[ ! -x "$ROOT/.venv/bin/python" ]]; then python3 -m venv "$ROOT/.venv"; fi
PY="$ROOT/.venv/bin/python"
export PIP_DISABLE_PIP_VERSION_CHECK=1
if ! "$PY" -c 'import paddle; assert paddle.is_compiled_with_cuda()' >/dev/null 2>&1; then
  "$PY" -m pip install --no-cache-dir \
    --find-links "$ROOT/wheel-cache" \
    --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    --extra-index-url https://www.paddlepaddle.org.cn/packages/stable/cu126/ \
    paddlepaddle-gpu==3.3.0
fi
"$PY" -m pip install --no-cache-dir \
  -i https://pypi.tuna.tsinghua.edu.cn/simple \
  "paddleocr==3.3.2" "fastapi>=0.115,<1" "uvicorn>=0.30,<1" \
  "pillow>=10,<13" "numpy>=1.24,<3" "tokenizers>=0.20,<1" "ftfy>=6,<7"
"$PY" - <<'PY'
import paddle, paddleocr
print("paddle:", paddle.__version__)
print("paddleocr:", paddleocr.__version__)
print("CUDA:", paddle.is_compiled_with_cuda())
print("device:", paddle.device.get_device())
PY

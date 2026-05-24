#!/usr/bin/env bash
set -euo pipefail

# 1. Initialize conda for this subshell
source "$(conda info --base)/etc/profile.d/conda.sh"

# 2. Now activate will work
cd /home/zengl/projects/SciCodePilot
conda activate scicodepilot-dev

RUN_DIR="artifacts/repro_bundle/$(date +%Y%m%d_%H%M%S)"
mkdir -p "${RUN_DIR}"

git rev-parse HEAD > "${RUN_DIR}/git_commit.txt" 2>/dev/null || echo "No git commit found" > "${RUN_DIR}/git_commit.txt"
git status --porcelain > "${RUN_DIR}/git_status.txt" 2>/dev/null || true
python -V > "${RUN_DIR}/python_version.txt"
uname -a > "${RUN_DIR}/uname.txt"

conda env export --from-history > "${RUN_DIR}/env.from_history.yml"
conda list --explicit > "${RUN_DIR}/env.explicit.txt"
pip freeze > "${RUN_DIR}/pip_freeze.txt"

if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv \
    > "${RUN_DIR}/gpu_info.csv"
fi

docker version > "${RUN_DIR}/docker_version.txt" 2>/dev/null || true
docker images --digests > "${RUN_DIR}/docker_images.txt" 2>/dev/null || true


#!/usr/bin/env bash
set -euo pipefail

cp -n .env.example .env || true

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

pushd frontend >/dev/null
npm install
popd >/dev/null

echo "Bootstrap complete."

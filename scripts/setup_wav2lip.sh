#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODELS_DIR="$ROOT_DIR/models"
WAV2LIP_DIR="$MODELS_DIR/Wav2Lip"
CHECKPOINT_DIR="$MODELS_DIR/wav2lip"

mkdir -p "$MODELS_DIR" "$CHECKPOINT_DIR"

if [ ! -d "$WAV2LIP_DIR" ]; then
  git clone https://github.com/Rudrabha/Wav2Lip.git "$WAV2LIP_DIR"
fi

if [ ! -f "$CHECKPOINT_DIR/wav2lip_gan.pth" ]; then
  echo "Download the checkpoint and place it at $CHECKPOINT_DIR/wav2lip_gan.pth"
  echo "Official link is provided in Wav2Lip README under pretrained models."
fi

echo "Wav2Lip setup complete."

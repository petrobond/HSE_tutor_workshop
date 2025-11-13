#!/usr/bin/env bash
set -Eeuo pipefail

HOST="51.250.28.165"
USER="yc-user"
KEY="/home/petr/yc_key"

LOCAL="/home/petr/projects/bash-scripts/"
REMOTE="/home/yc-user/projects/bash-scripts/"

notify() {
  if command -v notify-send >/dev/null 2>&1; then
    notify-send "$1"
  else
    echo "$1"
  fi
}

if rsync -az --delete \
  -e "ssh -i $KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
  "$LOCAL" "$USER@$HOST:$REMOTE"; then
  notify " Синхронизация завершена: $LOCAL → $USER@$HOST:$REMOTE"
else
  rc=$?
  notify "Ошибка синхронизации (код $rc)"
  exit "$rc"
fi


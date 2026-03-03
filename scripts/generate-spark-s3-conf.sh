#!/usr/bin/env bash
# Генерирует блок spark-defaults.conf для S3 из scripts/s3-credentials.env.
# Использование:
#   ./scripts/generate-spark-s3-conf.sh                    # вывести в stdout
#   ./scripts/generate-spark-s3-conf.sh > /tmp/s3.conf     # сохранить и передать на ВМ

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRED="${SCRIPT_DIR}/s3-credentials.env"

if [[ ! -f "$CRED" ]]; then
  echo "Файл $CRED не найден. Создайте его по образцу из object-storage-and-zeppelin-setup.md" >&2
  exit 1
fi

# shellcheck source=.
source "$CRED"

if [[ -z "$ACCESS_KEY_ID" || -z "$SECRET_KEY" ]]; then
  echo "В $CRED должны быть заданы ACCESS_KEY_ID и SECRET_KEY" >&2
  exit 1
fi

cat <<EOF
# Yandex Object Storage (S3) — сгенерировано $(date -u +"%Y-%m-%d %H:%M:%S UTC")
spark.hadoop.fs.s3a.endpoint            https://storage.yandexcloud.net
spark.hadoop.fs.s3a.path.style.access   true
spark.hadoop.fs.s3a.access.key           $ACCESS_KEY_ID
spark.hadoop.fs.s3a.secret.key          $SECRET_KEY
spark.hadoop.fs.s3a.impl                org.apache.hadoop.fs.s3a.S3AFileSystem
spark.hadoop.fs.s3a.connection.ssl.enabled true
EOF

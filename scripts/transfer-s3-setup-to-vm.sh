#!/usr/bin/env bash
# Копирует на ВМ yc-tutor:
#   1) s3-credentials.env — в домашний каталог (для ручной подстановки в Zeppelin и т.п.)
#   2) сгенерированный фрагмент spark-defaults.conf — в ~/spark-defaults-s3.conf
# На ВМ потом выполнить вручную:
#   sudo tee -a /opt/spark/conf/spark-defaults.conf < ~/spark-defaults-s3.conf
# Или раскомментировать блок ниже для автоматического добавления в конфиг Spark на ВМ.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ ! -f s3-credentials.env ]]; then
  echo "Файл s3-credentials.env не найден. Создайте его по object-storage-and-zeppelin-setup.md" >&2
  exit 1
fi

VM="${1:-yc-tutor}"
echo "Передача данных на ВМ: $VM"

scp s3-credentials.env "$VM":~/s3-credentials.env
./generate-spark-s3-conf.sh | ssh "$VM" 'cat > ~/spark-defaults-s3.conf'

echo "Готово. На ВМ:"
echo "  - ~/s3-credentials.env — переменные BUCKET, ACCESS_KEY_ID, SECRET_KEY"
echo "  - ~/spark-defaults-s3.conf — фрагмент для Spark"
echo ""
echo "Чтобы добавить S3-настройки в Spark на ВМ:"
echo "  ssh $VM 'sudo tee -a /opt/spark/conf/spark-defaults.conf < ~/spark-defaults-s3.conf'"
echo ""
echo "Zeppelin: Interpreter → spark → задать spark.hadoop.fs.s3a.* (значения из ~/s3-credentials.env)."

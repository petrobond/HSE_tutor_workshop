#!/bin/bash
# Команды для выполнения на ВМ (фазы 4–6 плана mart_city_top_products).
# Запускать по шагам или целиком после SSH на ВМ: ssh -i ~/.ssh/yc_key <user>@<public_ip>

set -e

# Без интерактивных диалогов (обновление ядра, needrestart и т.п.)
export DEBIAN_FRONTEND=noninteractive
export NEEDRESTART_MODE=a  # автоматический режим needrestart (a=all noninteractive)

# --- Фаза 4.1: базовая настройка ОС ---
sudo -E apt update
sudo -E apt upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"
sudo -E apt install -y openjdk-11-jdk python3 python3-pip git curl wget

# --- Фаза 4.2: Apache Spark ---
# Скачать и распаковать Spark (подставьте нужную версию, например 3.5.3)
SPARK_VER="3.5.3"
HADOOP_VER="3"
if [ ! -d /opt/spark ]; then
  sudo mkdir -p /opt
  cd /tmp
  wget -q "https://archive.apache.org/dist/spark/spark-${SPARK_VER}/spark-${SPARK_VER}-bin-hadoop${HADOOP_VER}.tgz"
  sudo tar -xzf "spark-${SPARK_VER}-bin-hadoop${HADOOP_VER}.tgz" -C /opt
  sudo mv "/opt/spark-${SPARK_VER}-bin-hadoop${HADOOP_VER}" /opt/spark
  rm -f "spark-${SPARK_VER}-bin-hadoop${HADOOP_VER}.tgz"
fi

# Переменные окружения Spark
if ! grep -q 'SPARK_HOME' ~/.bashrc; then
  echo 'export SPARK_HOME=/opt/spark' >> ~/.bashrc
  echo 'export PATH=$SPARK_HOME/bin:$PATH' >> ~/.bashrc
fi
export SPARK_HOME=/opt/spark
export PATH=$SPARK_HOME/bin:$PATH

# Проверка Spark
/opt/spark/bin/pyspark --version || true

# --- Фаза 4.3: Zeppelin ---
# Установка Zeppelin (пример для 0.10.2)
ZEPPELIN_VER="0.10.2"
if [ ! -d /opt/zeppelin ]; then
  cd /tmp
  wget -q "https://archive.apache.org/dist/zeppelin/zeppelin-${ZEPPELIN_VER}/zeppelin-${ZEPPELIN_VER}-bin-all.tgz"
  sudo tar -xzf "zeppelin-${ZEPPELIN_VER}-bin-all.tgz" -C /opt
  sudo mv "/opt/zeppelin-${ZEPPELIN_VER}-bin-all" /opt/zeppelin
  rm -f "zeppelin-${ZEPPELIN_VER}-bin-all.tgz"
fi

# Запуск Zeppelin (в фоне; для production лучше systemd)
# /opt/zeppelin/bin/zeppelin-daemon.sh start
# Веб-интерфейс: http://<public_ip>:8080

# --- Фаза 5.2: каталог для HDFS/локального пути ---
sudo mkdir -p /tmp/sandbox_zeppelin/mart_city_top_products
sudo chown -R "$(whoami):$(whoami)" /tmp/sandbox_zeppelin

echo "Фазы 4.1–4.3 и 5.2 подготовлены. Zeppelin запустите вручную: /opt/zeppelin/bin/zeppelin-daemon.sh start"

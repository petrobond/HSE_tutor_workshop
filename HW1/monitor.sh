# 1. Сбор метрик
echo "=== СТАТУС СИСТЕМЫ ($(date)) ==="

# Загрузка CPU (средняя за 1 минуту)
load1=$(cut -d' ' -f1 /proc/loadavg)
echo "CPU load (1 min avg): $load1"

# Память
read -r _ total used free shared buff cache avail < <(free -m | awk 'NR==2 {print "mem", $2, $3, $4, $5, $6, $7, $8}')
mem_percent=$(( used * 100 / total ))
echo "Memory: ${used}MiB / ${total}MiB (${mem_percent}%)"

# Диск (по корневому /)
disk_line=$(df -h / | awk 'NR==2')
disk_used=$(echo "$disk_line" | awk '{print $3 "/" $2 " (" $5 ")"}')
echo "Disk (/): $disk_used"
echo

# 2. Проверка порога памяти
threshold=80
if (( mem_percent > threshold )); then
  echo "!!! ВНИМАНИЕ: использование памяти > ${threshold}% (${mem_percent}%)"
  echo "Топ процессов по памяти:"
  # PID, %MEM, %CPU, RSS, команда
  ps -eo pid,pmem,pcpu,rss,comm --sort=-pmem | head -n 10
else
  echo "Память в норме (<= ${threshold}%)."
fi

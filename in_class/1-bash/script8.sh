IP=51.250.80.191
ping -c1 -W1 "$IP" >/dev/null 2>&1 && echo "$IP доступен" || echo "$IP недоступен"

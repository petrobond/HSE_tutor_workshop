HOST="51.250.28.165"
USER="yc-user"
KEY="/home/petr/yc_key"
THRESH=10  

read -r USED_PCT MNT <<<"$(
  ssh -i "$KEY" -o ConnectTimeout=5 \
      -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
      "$USER@$HOST" \
      "df -P / | awk 'NR==2{gsub(/%/,\"\",\$5); print \$5, \$6}'"
)"

FREE=$((100 - USED_PCT))

if (( FREE < THRESH )); then
  echo "ало места: свободно ${FREE}% на ${MNT} (порог ${THRESH}%)."
  exit 1
else
  echo " Ок: свободно ${FREE}% на ${MNT}."
fi


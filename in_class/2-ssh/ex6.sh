HOST="51.250.28.165"
USER="yc-user"
KEY="/home/petr/yc_key"


read -rp "Команда: " CMD

echo "— Локально:"
bash -lc "$CMD"

echo -e "\n— Удалённо:"
ssh -i "$KEY" "$USER@$HOST" "bash -lc $(printf '%q' "$CMD")"

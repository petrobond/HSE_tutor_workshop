TEXT='Привет!'

curl -sS "https://api.telegram.org/bot${TOKEN}/getMe"

curl -sS -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  --data-urlencode chat_id="$CHAT_ID" \
  --data-urlencode text="$TEXT"

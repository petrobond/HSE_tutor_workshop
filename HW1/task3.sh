read -r -p "Введите целое число: " n

if   (( n > 0 )); then
  echo "Число положительное."
  i=1
  while (( i <= n )); do
    echo "$i"
    ((i++))
  done
elif (( n < 0 )); then
  echo "Число отрицательное."
else
  echo "Это ноль."
fi

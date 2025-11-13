read -rp "Введите два числа: " a b
if ((a>b)); then echo "$a > $b"; elif ((a<b)); then echo "$a < $b"; else echo "$a = $b"; fi

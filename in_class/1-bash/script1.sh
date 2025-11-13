read -rp "Введите ваше имя: " name
read -rp "Введите ваш возраст: " age

next_age=$((age + 1))
echo "Привет, $name! Через год тебе будет $next_age лет."

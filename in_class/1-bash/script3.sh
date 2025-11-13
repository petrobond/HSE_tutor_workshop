read -rp "Введите путь к директории: " dir

name="$(basename "$dir")_$(date +%Y-%m-%d).tar.gz"

# Архив создаётся в текущей папке запуска скрипта
tar -czf "$name" -C "$(dirname "$dir")" "$(basename "$dir")"

echo "Готово: $name"


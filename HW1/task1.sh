# 1) Список всех объектов в текущей директории с типом
echo "== Список с типами =="
for f in *; do
  [[ -e "$f" ]] || continue
  printf '%s — %s\n' "$f" "$(stat -c %F -- "$f")"
done

# 2) Проверка наличия файла, переданного как аргумент
target="${1:-}"
if [[ -z "$target" ]]; then
  echo "Использование: $0 <имя_файла>" >&2
else
  if [[ -e "$target" ]]; then
    echo "OK: '$target' существует."
  else
    echo "Нет: '$target' отсутствует."
  fi
fi

# 3) Цикл for: имя и права доступа каждого файла/каталога
echo "== Имя и права доступа =="
for f in *; do
  [[ -e "$f" ]] || continue
  printf '%s — %s\n' "$f" "$(stat -c %A -- "$f")"
done

# Использование:
#   ./backup.sh /откуда /куда [лог-файл]
#
# Пример:
#   ./backup.sh ~/docs ~/docs_backup backup.log

src="${1:-}"
dst="${2:-}"
logfile="${3:-backup.log}"

if [[ -z "$src" || -z "$dst" || ! -d "$src" ]]; then
  echo "Использование: $0 <директория_источник> <директория_бэкапа> [лог-файл]" >&2
  exit 1
fi

# создадим папку назначения, если её нет
mkdir -p "$dst"

date_str="$(date +%Y-%m-%d)"
count=0

{
  echo "=== $(date) ==="
  echo "Резервное копирование из: $src"
  echo "В директорию: $dst"
  for f in "$src"/*; do
    [[ -f "$f" ]] || continue  # только обычные файлы
    base="$(basename "$f")"
    backup_name="${base}.${date_str}.bak"
    cp -- "$f" "$dst/$backup_name"
    echo "Копия: $base -> $dst/$backup_name"
    ((count++))
  done
  echo "Всего файлов скопировано: $count"
  echo
} >> "$logfile"

echo "Готово: скопировано $count файл(ов). Лог: $logfile"

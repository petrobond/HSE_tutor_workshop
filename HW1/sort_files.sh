# Использование: ./sort_files.sh /путь/к/директории /путь/к/log.txt
dir="${1:-}"
logfile="${2:-/var/log/sort_files.log}"

if [[ -z "$dir" || ! -d "$dir" ]]; then
  echo "Использование: $0 <директория> [лог-файл]" >&2
  exit 1
fi

img_dir="$dir/Images"
doc_dir="$dir/Documents"

mkdir -p "$img_dir" "$doc_dir"

timestamp="$(date '+%Y-%m-%d %H:%M:%S')"

# функция перемещения с логированием
move_files() {
  pattern="$1"
  target="$2"
  for f in "$dir"/*.$pattern; do
    [[ -e "$f" ]] || continue
    base="$(basename "$f")"
    mv -- "$f" "$target/$base"
    echo "[$timestamp] Moved $base -> $target/" >> "$logfile"
  done
}

# Картинки
move_files jpg "$img_dir"
move_files png "$img_dir"
move_files gif "$img_dir"

# Документы
move_files txt  "$doc_dir"
move_files pdf  "$doc_dir"
move_files docx "$doc_dir"

# Настройка cron:

# crontab -e

# 0 2 * * * /home/petr/projects/HSE_tutor_workshop/HW1/sort_files.sh /home/petr/projects/HSE_tutor_workshop/HW1/Downloads /home/petr/projects/HSE_tutor_workshop/HW1/sort.log

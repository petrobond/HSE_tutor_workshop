read -rp "Введите имя файла: " file_name

if [ -f "$file_name" ]; then
echo "Файл существует"
else
echo "Файл не найден"
fi

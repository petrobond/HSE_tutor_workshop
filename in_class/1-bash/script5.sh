read -rp "Введите имя файла: " file
read -rp "Введите слово для поиска: " word
grep -owF -- "$word" "$file" | wc -l

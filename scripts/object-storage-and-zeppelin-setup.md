# Ручная настройка Object Storage (S3) и интерпретатора Zeppelin

Выполнять на ВМ после установки Spark и Zeppelin (скрипт `vm-setup-phases-4-6.sh`).

---

## Часть 1. Object Storage в Yandex Cloud

### 1.1. Создать бакет

**Через консоль:** [Yandex Cloud Console](https://console.cloud.yandex.ru) → Object Storage → Создать бакет.

- Имя: например `hse-spark-mart-<ваш-login>` (уникальное в рамках облака).
- Класс хранения: стандартный.
- Доступ: ограниченный (приватный) — доступ будет по ключам.

**Через CLI (если установлен `yc` на ВМ или локально):**
```bash
yc storage bucket create --name hse-spark-mart-<login>
```

### 1.2. Сервисный аккаунт и статические ключи

1. В консоли: **IAM** → **Сервисные аккаунты** → **Создать**.
   - Имя, например: `spark-s3`.
   - Назначить роль: **storage.editor** (или **storage.admin** для простоты).

2. Выдать ключи доступа для этого сервисного аккаунта:
   - Открыть сервисный аккаунт → вкладка **Статические ключи доступа** → **Создать ключ**.
   - Сохранить **Access Key ID** и **Secret Key** — они понадобятся на ВМ (секрет в коде не коммитить).

3. Права на бакет: если бакет в том же каталоге и у сервисного аккаунта роль на каталог (например, storage.editor), дополнительная настройка не нужна. Иначе в настройках бакета выдать доступ этому сервисному аккаунту.

---

## Часть 2. Настройка Spark на ВМ для доступа к S3

Spark должен знать, как подключаться к Yandex Object Storage (S3-совместимый API).

### 2.1. Файл конфигурации Spark

Создать или дополнить конфиг, который подхватывается Spark при запуске из Zeppelin. Удобно положить настройки в `$SPARK_HOME/conf/spark-defaults.conf` или передавать через интерпретатор Zeppelin (см. ниже).

**На ВМ выполнить (подставьте свои ключи и имя бакета):**

```bash
sudo tee -a /opt/spark/conf/spark-defaults.conf << 'EOF'

# Yandex Object Storage (S3)
spark.hadoop.fs.s3a.endpoint            https://storage.yandexcloud.net
spark.hadoop.fs.s3a.path.style.access   true
spark.hadoop.fs.s3a.access.key           <ACCESS_KEY_ID>
spark.hadoop.fs.s3a.secret.key          <SECRET_KEY>
spark.hadoop.fs.s3a.impl                org.apache.hadoop.fs.s3a.S3AFileSystem
spark.hadoop.fs.s3a.connection.ssl.enabled true
EOF
```

Замените `<ACCESS_KEY_ID>` и `<SECRET_KEY>` на ключи из п. 1.2.

**Вариант без записи секретов в файл:** задать эти же параметры только в настройках интерпретатора Zeppelin (см. часть 3), тогда в `spark-defaults.conf` можно не писать ключи.

### 2.2. Зависимость hadoop-aws

Spark 3.x обычно уже включает поддержку S3A. Если при обращении к `s3a://...` будет ошибка про класс или протокол, при запуске Zeppelin/Spark нужно добавить пакет, например в интерпретаторе Zeppelin (см. ниже):

- `spark.jars.packages` = `org.apache.hadoop:hadoop-aws:3.3.4`  
(версию подберите под ваш Hadoop в Spark: посмотреть можно в `/opt/spark/jars` по имени hadoop-*.)

---

## Часть 3. Настройка интерпретатора Zeppelin

### 3.1. Открыть настройки интерпретатора

1. В браузере: `http://<публичный_IP_ВМ>:8080`.
2. Вверху: **Anonymous** (или ваш пользователь) → **Interpreter**.
3. Найти **spark** (или **spark2**) и нажать **Edit** (карандаш).

### 3.2. Параметры интерпретатора

В форме редактирования задать (или проверить) свойства:

| Свойство | Значение | Комментарий |
|----------|----------|-------------|
| **master** | `local[*]` | Локальный Spark, все ядра |
| **spark.app.name** | `Zeppelin` | По желанию |

Чтобы Spark видел S3, добавьте в те же настройки (кнопка «+» или отдельные поля, в зависимости от версии Zeppelin) свойства вида **Property** / **Value**:

| Property | Value |
|----------|--------|
| `spark.hadoop.fs.s3a.endpoint` | `https://storage.yandexcloud.net` |
| `spark.hadoop.fs.s3a.path.style.access` | `true` |
| `spark.hadoop.fs.s3a.access.key` | ваш Access Key ID |
| `spark.hadoop.fs.s3a.secret.key` | ваш Secret Key |
| `spark.hadoop.fs.s3a.impl` | `org.apache.hadoop.fs.s3a.S3AFileSystem` |

Если в `spark-defaults.conf` на ВМ уже прописаны эти ключи и endpoint, в интерпретаторе можно задать только `master` и при необходимости `spark.jars.packages` — остальное подхватится из конфига.

### 3.3. Использование PySpark

- В ноутбуке для ячеек Spark на Python выберите интерпретатор **%spark.pyspark** (или создайте интерпретатор с таким именем на базе spark).
- После сохранения настроек нажмите **Save** и при запросе **Restart** перезапустите интерпретатор.

### 3.4. Проверка из ноутбука

В новом параграфе Zeppelin:

```python
%spark.pyspark
# Spark
spark.range(5).show()
# Путь к вашему бакету (создайте папку в консоли при необходимости)
spark.read.parquet("s3a://hse-spark-mart-<login>/mart_city_top_products/").show()
# или просто запись тестового датафрейма
spark.range(10).write.mode("overwrite").parquet("s3a://hse-spark-mart-<login>/test/")
spark.read.parquet("s3a://hse-spark-mart-<login>/test/").show()
```

Если чтение/запись проходят без ошибок, S3 и интерпретатор настроены верно.

---

## Кратко: что куда подставлять

| Место | Что подставить |
|-------|-----------------|
| `hse-spark-mart-<login>` | Имя вашего бакета в Object Storage |
| `<ACCESS_KEY_ID>` | Access Key ID статического ключа сервисного аккаунта |
| `<SECRET_KEY>` | Secret Key того же ключа |
| `<публичный_IP_ВМ>` | Публичный IP вашей ВМ в Yandex Cloud |

Секреты (ключи) не добавляйте в репозиторий и не коммитьте в git.

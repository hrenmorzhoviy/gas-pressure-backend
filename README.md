# Газовый каталог — лабораторные работы №2–3

Проект посвящён каталогу газов и параметрам, используемым при расчёте давления. Ветка `rest_api` продолжает лабораторную №2 и добавляет REST API на FastAPI без TypeScript.

## REST API лабораторной №3

Swagger доступен по адресу `http://localhost:8080/docs`. Во всех изменяющих методах текущий пользователь фиксирован функцией-зависимостью `get_current_user_id()` со значением `1`, как требует задание.

| Метод | URL | Назначение |
|---|---|---|
| GET | `/api/gases?molar_mass_min=&molar_mass_max=` | Опубликованные газы с серверной фильтрацией и признаком создателя |
| GET | `/api/gases/feed` | Первый опубликованный газ в ленте |
| GET | `/api/gases/feed?gas_id=5&next=true` | Следующий газ по фактическому ID с переходом через пропуски и закольцовыванием |
| GET | `/api/gases/draft` | Единственный черновик текущего пользователя |
| POST | `/api/gases/draft` | Создание/обновление черновика; `image` и `video` передаются файлами |
| PUT | `/api/gases/{id}/publish` | Разрешённый переход `draft → published` |
| DELETE | `/api/gases/{id}` | Мягкое удаление опубликованного газа его создателем |
| POST | `/api/gases/{id}/like?liked=1` | Поставить лайк; `liked=0` снимает его |
| POST | `/api/users/register` | Регистрация с Argon2-хешированием пароля |
| POST | `/api/users/login` | Заглушка для лабораторной №4 |
| POST | `/api/users/logout` | Заглушка для лабораторной №4 |

Поля `id`, `creator_id`, `status`, `created_at` и `published_at` не принимаются от клиента: их рассчитывает сервер. Необязательные поля услуги: `description`, `molar_mass`, `density`. Названия медиафайлов генерируются сервером на латинице, файлы сохраняются в MinIO.

## Таблицы

- `users`: `id`, `username`, `password_hash`.
- `gases`: тематические поля `name`, `description`, `molar_mass`, `density`; медиа `image_key`, `video_key`, `image_url`, `video_url`; системные поля `status`, `is_deleted`, `creator_id`, `created_at`, `published_at`.
- `likes`: `id`, `user_id`, `gas_id`; уникальная пара пользователя и газа.

Миграция `0002_rest_api_fields.py` добавляет пароль, создателя и даты к существующей схеме лабораторной №2. Статическая заглушка изображения лежит в `static/img/placeholder.svg`, поэтому интерфейс не зависит от MinIO для картинки по умолчанию.

В HTML-интерфейсе фото и видео выбираются стандартным окном проводника. Оба файла необязательны: без выбора используются `static/img/default.png` и `static/video/default.mp4`. На странице плиток нет кнопки лайка; управление лайком остаётся в ленте и REST API согласно заданию лабораторной №3.

## Стек
- **FastAPI** + **Jinja2** (шаблонизатор)
- **SQLAlchemy** 2.0 async + **asyncpg** (ORM, асинхронный)
- **Alembic** (миграции)
- **PostgreSQL 15** (основная БД)
- **Minio** (хранилище медиа)
- **Adminer** (веб-интерфейс к БД)
- **pydantic-settings** (конфигурация через .env)

## Что добавлено в Лабе 2 (по сравнению с Лабой 1)

| Функционал | Реализация |
|---|---|
| Данные из PostgreSQL вместо коллекции | SQLAlchemy ORM + asyncpg |
| Лайки (м-м users ↔ gases) | ORM: таблица `likes` |
| Мягкое удаление газа | Raw SQL через `text()` (курсор) |
| Добавление нового газа | POST /add/ через ORM |
| Публикация черновика | POST /publish/{id} через ORM |
| Миграции схемы БД | Alembic |
| Конфигурация через .env | pydantic-settings |

## Структура проекта

```
lab2/
├── alembic/                    # Миграции БД
│   ├── versions/
│   │   └── 0001_init_gases_users_likes.py
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── api/
│   └── handlers.py             # Все маршруты (5 контроллеров)
├── core/
│   └── config.py               # Pydantic Settings (.env)
├── db/
│   ├── base.py                 # DeclarativeBase
│   └── session.py              # Async engine + get_db()
├── models/
│   ├── gas.py                  # Таблица gases
│   ├── user.py                 # Таблица users
│   └── like.py                 # Таблица likes (м-м)
├── static/
│   ├── css/style.css
│   └── img/placeholder.svg
├── templates/
│   ├── gases.html              # Плитка + фильтр + лайк + удалить
│   ├── feed.html               # Лента с видео + лайк
│   └── add.html                # Добавление + публикация черновика
├── .env                        # Переменные окружения
├── docker-compose.yml          # PostgreSQL + Adminer + Minio
├── main.py
├── requirements.txt
└── seed.sql                    # Начальные данные
```

---

## Запуск

### 1. Запуск Docker-сервисов

```bash
cd lab2
docker-compose up -d
```

Проверить: `docker ps` — убедиться, что все три контейнера `Up`.

### 2. Установка зависимостей Python

```bash
cd lab2
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Настройка .env

Файл `.env` уже создан. Если PostgreSQL запущен через docker-compose из этого проекта — ничего менять не нужно.

```ini
DB_HOST=localhost
DB_PORT=5432
DB_USER=gasuser
DB_PASSWORD=gaspassword
DB_NAME=gas_db
MINIO_BASE=http://localhost:9000/media
```

### 4. Применение миграций (Alembic)

```bash
cd lab2
alembic upgrade head
```

После выполнения в БД появятся таблицы: `users`, `gases`, `likes`, `alembic_version`.

### 5. Загрузка начальных данных

Откройте **Adminer** по адресу `http://localhost:8081`:
- Система: PostgreSQL
- Сервер: `postgres`
- Пользователь: `gasuser`
- Пароль: `gaspassword`
- База данных: `gas_db`

Перейдите в «SQL-команда» и вставьте содержимое файла `seed.sql`, нажмите «Выполнить».

Или через psql:
```bash
psql postgresql://gasuser:gaspassword@localhost:5432/gas_db -f seed.sql
```

### 6. Запуск приложения

```bash
cd lab2
python main.py
```

Открыть в браузере: **http://localhost:8080**

---

## Маршруты (5 контроллеров)

| Метод | URL | Описание | Реализация |
|---|---|---|---|
| GET | `/gases/` | Плитка газов с фильтром | ORM SELECT |
| GET | `/feed/` | Лента (первый газ) | ORM SELECT |
| GET | `/feed/{gas_id}` | Лента по ID; `?next=true` — следующий | ORM SELECT через курсор |
| GET | `/add/` | Черновик / форма добавления | ORM SELECT |
| POST | `/add/` | Сохранить новый газ | ORM INSERT |
| POST | `/publish/{gas_id}` | Опубликовать черновик | ORM UPDATE |
| POST | `/delete/{gas_id}` | Мягкое удаление | Raw SQL `text()` (курсор) |
| POST | `/like/{gas_id}` | Лайк / снятие лайка | ORM INSERT/DELETE |

---

## Порядок показа (Лаба 2, скриншоты)

1. **Скриншоты 1-2**: Adminer → логически удалить газ через кнопку «Удалить» в интерфейсе → показать `SELECT * FROM gases` — поле `is_deleted = true`.
2. **Скриншоты 3-10**:
   - Показать 3 страницы с поиском (фильтр по молярной массе)
   - Удалить газ кнопкой → показать `SELECT` в БД
   - Перейти по URL удалённого газа → страница не показывается
   - Добавить новый газ через форму `/add/`
   - Показать `SELECT` в БД
   - Опубликовать черновик → `SELECT` снова
3. **Скриншоты 11-13**: В БД изменить `molar_mass`, `density` газа вручную → показать изменения в приложении. Изменить количество строк в `likes`.
4. **Скриншоты 14-21**: В коде показать модели (`gas.py`, `user.py`, `like.py`), 5 контроллеров через ORM, удаление через `SQL UPDATE` (`text()`).
5. **Скриншот 22**: Фото и видео по умолчанию в HTML (`/static/img/placeholder.svg`).

---

## ER-диаграмма (сделать самому в StarUML)

> ⚠️ Это нужно сделать САМОСТОЯТЕЛЬНО в StarUML или draw.io

Три таблицы:

```
users
  id        INTEGER PK
  username  VARCHAR(50) UNIQUE NOT NULL

gases
  id          INTEGER PK
  name        VARCHAR(100) NOT NULL
  molar_mass  FLOAT NOT NULL
  density     FLOAT NOT NULL
  description VARCHAR(1000) NOT NULL
  image_key   VARCHAR(255)
  video_key   VARCHAR(255)
  image_url   VARCHAR(512)
  video_url   VARCHAR(512)
  status      VARCHAR(20)   -- published | draft | deleted
  is_deleted  BOOLEAN

likes  (м-м между users и gases)
  id       INTEGER PK
  user_id  INTEGER FK → users.id
  gas_id   INTEGER FK → gases.id
  UNIQUE(user_id, gas_id)
```

Связи:
- `users` → `likes`: один ко многим (1 пользователь → много лайков)
- `gases` → `likes`: один ко многим (1 газ → много лайков)
- `users` ↔ `gases` через `likes`: **многие ко многим**

---

## Что нужно сделать САМОМУ

1. **ER-диаграмма в StarUML** (обязательно):
   - Создать файл StarUML
   - Добавить 3 таблицы со всеми полями, типами и размерами
   - Провести связи (FK) с указанием кардинальности (1..*, *..)
   - Указать PK и FK стрелками

2. **Minio** (опционально для демонстрации медиа):
   - Запустить через docker-compose (уже включён)
   - Открыть консоль: http://localhost:9001 (minioadmin/minioadmin)
   - Создать bucket `media`, сделать публичным
   - Загрузить изображения: nitrogen.jpg, oxygen.jpg, helium.jpg, argon.jpg, co2.jpg, hydrogen.jpg
   - Загрузить видео (опционально)

3. **Скриншоты для отчёта** (.doc файл по порядку показа выше)

4. **git-ветка**: создать ветку `lab2` и запушить код

---

## Контрольные вопросы (подготовить ответы)

- Виды БД, SQL запросы, курсоры
- ORM: назначение, преимущества и недостатки
- Модель и миграция (что такое Alembic)
- Чистая архитектура
- Что такое soft delete и зачем он нужен

# Blackburn DevBlog

Этот инструмент превращает Git-коммиты в удобочитаемые посты для devlog и может автоматически публиковать их в Telegram-канал через GitHub Webhooks.

## 🚀 Быстрый старт (5 минут)

### 1. Установка и подготовка окружения

```powershell
# Перейти в папку инструмента
cd tools/devblog

# Создать виртуальное окружение
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл (скопировать из шаблона и заполнить)
Copy-Item ..\..\\.env.example .env
# Отредактировать .env и заполнить:
# - TELEGRAM_BOT_TOKEN (получить у @BotFather в Telegram)
# - OPENAI_API_KEY (опционально, для улучшенной генерации)
# - GITHUB_WEBHOOK_SECRET_DEFAULT (любая случайная строка)
```

### 2. Инициализация базы данных

```powershell
# Инициализировать SQLite БД и создать первый проект
python scripts/bootstrap_blackburn_project.py
```

Скрипт выведет вам:
- ID проекта
- Webhook Secret (сохраните его!)
- Инструкции по настройке GitHub Webhook

### 3. Запуск сервера

```powershell
# Запустить FastAPI сервер
python main.py
# или с горячей перезагрузкой:
uvicorn app.main:app --reload
```

Сервер будет доступен по адресу `http://localhost:8000`

### 4. Настройка GitHub Webhook

```powershell
# Вывести инструкции для настройки вебхука
python scripts/print_webhook_instructions.py
```

Затем:
1. Перейди в https://github.com/Rudiak-Kirill/blackburn_tools/settings/hooks
2. Нажми **Add webhook**
3. Заполни значения как указано в выводе скрипта
4. Выбери только **Push events**

### 5. Тестирование локально (без GitHub)

```powershell
# Сгенерировать и отправить тестовый webhook
python scripts/simulate_webhook_blackburn.py --num-commits 3
```

Если всё верно — в Telegram канале `@blackburn_devblog` появится пост! 🎉

---

## 📚 Полная документация

### Архитектура

```
GitHub (Push Event)
       ↓
WebhookHandler (POST /webhook/github)
       ↓
CommitProcessor (валидация, фильтрация)
       ↓
ContentGenerator (OpenAI или шаблон)
       ↓
TelegramService (отправка в канал)
       ↓
Database (SQLite/PostgreSQL)
```

### Компоненты

| Модуль | Описание |
|--------|---------|
| `app/api/webhook.py` | Endpoint для получения GitHub webhooks |
| `app/api/projects.py` | REST API для управления проектами |
| `app/api/admin.py` | HTML интерфейс админа |
| `app/services/commit_processor.py` | Обработка коммитов, фильтрация, отправка |
| `app/services/content_generator.py` | Генерация текста поста (AI + шаблон) |
| `app/integrations/openai_service.py` | OpenAI API интеграция |
| `app/integrations/telegram.py` | Telegram Bot API с rate limiting |

### Фильтрация коммитов

По умолчанию обрабатываются коммиты с префиксами:
- `feat:` → новые фичи (✨)
- `fix:` → исправления ошибок (🐛)
- `docs:` → документация (📚)
- `perf:` → оптимизация производительности (⚡)
- `refactor:` → рефакторинг (♻️)
- `test:` → тесты (🧪)
- `chore:` → служебные изменения (🔧)

Пропускаются merge commits и коммиты вне указанной ветки.

### Управление проектами

#### Через CLI

```powershell
# Список всех проектов
python scripts/manage_projects.py list

# Показать детали проекта
python scripts/manage_projects.py show <project-id>

# Создать новый проект
python scripts/manage_projects.py create \
  --name "My Project" \
  --repo "owner/repo" \
  --chat-id "@channel_name" \
  --ai-enabled

# Обновить проект
python scripts/manage_projects.py update <project-id> \
  --name "Updated Name"

# Включить/выключить AI
python scripts/manage_projects.py toggle-ai <project-id>

# Удалить проект
python scripts/manage_projects.py delete <project-id>
```

#### Через HTML админку

```
http://localhost:8000/admin/projects
```

Если установлен `ADMIN_API_KEY` в `.env` — потребует авторизацию.

### Переменные окружения

```env
# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_RATE_LIMIT_PER_MIN=30

# OpenAI (опционально)
OPENAI_API_KEY=sk-...

# GitHub
GITHUB_WEBHOOK_SECRET_DEFAULT=some-random-secret

# База данных
DATABASE_URL=sqlite:///./blackburn_tools.db
# или: postgresql://user:pass@localhost/blackburn_db

# Админ
ADMIN_API_KEY=your-secret-key

# Приложение
APP_ENV=development
LOG_LEVEL=info
```

### Примеры постов

**Шаблонный пост** (без AI):
```
🚀 Blackburn Tools — 3 коммита

✨ [FEAT] Add webhook signature validation
🐛 [FIX] Handle missing commit messages gracefully  
📚 [DOCS] Update integration documentation

12.01.2024 в 15:30

#devblog #blackburn_tools
```

**AI-сгенерированный пост** (с OpenAI):
```
🚀 Blackburn Tools — 2 коммита

Реализована валидация GitHub webhook с использованием HMAC-SHA256.
Улучшена обработка ошибок при отсутствии сообщений коммитов.

✨ Add webhook signature validation
🐛 Handle missing commit messages gracefully

12.01.2024 в 15:30

#devblog #blackburn_tools
```

---

## 🔒 Безопасность

- ✅ Все webhook подписаны HMAC-SHA256 (GitHub специфика)
- ✅ Секреты хранятся в `.env` файле (`.env` в `.gitignore`)
- ✅ Rate limiting для Telegram API (по умолчанию 30 сообщений/минуту)
- ✅ Token-bucket алгоритм в памяти
- ✅ Админ-интерфейс защищен `ADMIN_API_KEY`

---

## 🌐 Для публичного развертывания (не localhost)

### Через ngrok (быстро для тестирования)

```powershell
# Установить ngrok: https://ngrok.com

# Запустить туннель на порт 8000
ngrok http 8000

# Копировать https URL и использовать как Payload URL в GitHub
# Например: https://12ab-345-67-89.ngrok.io/webhook/github
```

### На Production (например Heroku, Railway, Render)

1. Создать Docker контейнер (Dockerfile TBD)
2. Установить environment variables в UI хостинга
3. Добавить GitHub Webhook с production URL
4. Настроить базу данных (PostgreSQL рекомендуется)

---

## 🐛 Отладка

### Логи сервера

```powershell
# Проверить логи в консоли (если APP_ENV=development)
python main.py

# Или в файле логов (если настроено)
Get-Content logs/devblog.log -Tail 50
```

### Проверить БД

```powershell
# Установить DBeaver или другой SQL клиент
# И подключиться к sqlite:///./blackburn_tools.db

# Или из PowerShell (если установлен sqlite3):
sqlite3 blackburn_tools.db
> .tables
> SELECT * FROM project;
```

### Тестовый webhook с отладкой

```powershell
python scripts/simulate_webhook_blackburn.py --num-commits 5 --server-url http://localhost:8000
```

---

## 📝 Примечания

- API доступен в `app/api` (FastAPI).
- HTML-админка доступна по `/admin/projects` (защищается `ADMIN_API_KEY`, если задан).
- Для управления проектами локально можно использовать CLI-утилиту: `scripts/manage_projects.py`.

Если вы используете приватные enterprise-модули, добавляйте их как submodule в `tools/devblog/enterprise/` или устанавливайте из приватного PyPI. См. `PRIVATE_MODULES.md` в корне репозитория.

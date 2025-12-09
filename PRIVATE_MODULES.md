# Подключение приватного репозитория как модуля

Этот документ описывает поддерживаемые способы подключения приватных/enterprise-модулей к публичному open-core репозиторию. Выберите подходящий метод в зависимости от ваших процессов деплоя и политики безопасности.

1) Git Submodule (рекомендуется для строго привязанного к конкретному коммиту модуля)

- Добавить submodule:

```powershell
git submodule add git@github.com:your-org/your-private-module.git enterprise/your-private-module
git commit -m "Add private module submodule"
```

- Инициализация/обновление при клоне:

```powershell
git clone git@github.com:your-org/blackburn_tools.git
cd blackburn_tools
git submodule update --init --recursive
```

Плюсы: версия привязана к конкретному коммиту; легко контролировать обновления.
Минусы: требует прав доступа к приватному репозиторию для всех, кто хочет собрать проект.

2) Git Subtree (альтернатива без отдельного .gitmodules)

- Добавить subtree:

```powershell
git remote add private git@github.com:your-org/your-private-module.git
git subtree add --prefix=enterprise/your-private-module private main --squash
```

Обновление:

```powershell
git subtree pull --prefix=enterprise/your-private-module private main --squash
```

3) pip install из приватного репозитория (SSH)

- Установить пакет напрямую из Git (понадобится доступ по SSH):

```powershell
pip install git+ssh://git@github.com/your-org/your-private-module.git@main#egg=your_private_module
```

В `requirements-private.txt` можно указать такую строку и устанавливать зависимости отдельно.

4) pip install из приватного репозитория (HTTPS + token) — НЕ РЕКОМЕНДУЕТСЯ

- Пример (не храните токены в репозитории):

```powershell
pip install "git+https://<TOKEN>@github.com/your-org/your-private-module.git@main#egg=your_private_module"
```

5) Частный PyPI / приватный индекс пакетов

- В зависимости от политики организации, можно публиковать приватные колеса и указывать `--extra-index-url` при установке.

6) Подключение в коде

- Если вы используете локальные модули (например помещаете код в `enterprise/your-private-module`), добавьте их в `PYTHONPATH` или установите в editable режиме:

```powershell
pip install -e enterprise/your-private-module
```

7) Как хранить приватные конфигурации

- Не храните секреты в публичном репозитории.
- Используйте переменные окружения, секретные менеджеры (Vault, GitHub Secrets) или конфигурацию в закрытом репозитории.

8) Рекомендации по CI/CD

- Для сборки в CI используйте deploy-ключи, machine users или интеграции, дающие доступ только к необходимым приватным репозиториям.
- Держите шаги и переменные с токенами только в защищённых секретах CI.

9) Игнорирование приватных модулей в публичном репозитории

- В `.gitignore` перечислены папки, где обычно располагают приватные модули (`enterprise/`, `private_modules/` и т.д.). Не добавляйте приватный код в публичный репозиторий.

10) Пример быстрой настройки для разработчика

```powershell
# 1) Клонируем публичный репозиторий
git clone git@github.com:your-org/blackburn_tools.git
cd blackburn_tools

# 2) Инициализируем submodule (если используется)
git submodule update --init --recursive

# 3) Устанавливаем зависимости
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 4) Если приватный модуль присутствует локально, установить в editable режиме
pip install -e enterprise/your-private-module
```

Если хотите, могу подготовить пример CI-конфигурации (GitHub Actions) для автоматического доступа к приватным модулям.

CI (GitHub Actions) — доступ к приватным submodule

Примерный подход для CI, чтобы workflow мог клонировать приватные подмодули:

1) Создайте приватный SSH-ключ (deploy key) или machine user с SSH-ключом, который имеет доступ на чтение к приватным репозиториям (private modules).

2) Добавьте приватный ключ как `Secret` в настройках репозитория `Settings -> Secrets -> Actions` (имя, например, `SSH_PRIVATE_KEY`).

3) Пример workflow (фрагмент) — полный пример в `.github/workflows/ci-private.yml`:

```yaml
uses: actions/checkout@v4
with:
	submodules: 'false'

# установить ssh-агент и добавить секретный ключ
uses: webfactory/ssh-agent@v0.5.4
with:
	ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

# гарантируем known_hosts
run: ssh-keyscan github.com >> ~/.ssh/known_hosts

# затем инициализируем submodules
run: git submodule update --init --recursive
```

4) Безопасность:
- Дайте ключу доступ только к нужным приватным репозиториям.
- Рассмотрите использование machine user с ограниченными правами или deploy keys, привязанных к отдельным приватным репо.

5) Альтернативы:
- Использовать GitHub App или deploy tokens с правильными правами.
- Настроить частный PyPI и хранить учетные данные в секрете CI.

Если нужно, могу подготовить пример workflow с более подробной обработкой (known_hosts, проверкой fingerprint, fallback на machine user и т.д.).